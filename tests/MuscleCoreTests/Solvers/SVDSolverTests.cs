using MuscleCore.Solvers;
using MuscleCore.FEModel;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Python.Runtime;
using System.IO;
using System;
using MuscleCore.PythonNETInit;

namespace MuscleCoreTests.Solvers
{
    [TestClass]
    public class SVDSolverTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private FEM_Structure _structure;

        [TestInitialize]
        public void Initialize()
        {
            condaEnvPath = PythonNETConfig.condaEnvPath;
            pythonDllName = PythonNETConfig.pythonDllName;

            srcDir = Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(),
             "..", "..", "..", "..", "..", "src"));

            PythonNETManager.Initialize(condaEnvPath, pythonDllName, srcDir);
            
            // Set up the 2-cable structure for testing
            // Create nodes
            var nodes = new FEM_Nodes(
                initialCoordinates: new double[,] {
                    { 0.0, 0.0, 0.0 },  // Node 0
                    { 1.0, 0.0, 0.0 },  // Node 1
                    { 2.0, 0.0, 0.0 }   // Node 2
                },
                dof: new bool[,] {
                    { false, false, false },  // Node 0: fixed
                    { true, true, true },     // Node 1: free in x,y,z
                    { false, false, false }   // Node 2: fixed
                }
            );

            // Create elements (cables)
            var elements = new FEM_Elements(
                nodes: nodes,
                type: new int[] { 1, 1 },  // Two cables (type 1)
                endNodes: new int[,] { { 0, 1 }, { 1, 2 } }  // Element 0: 0->1, Element 1: 1->2
            );

            // Create structure
            _structure = new FEM_Structure(nodes, elements);
        }

        [TestCleanup]
        public void Cleanup()
        {
            PythonNETManager.ShutDown();
        }

        [TestMethod]
        public void Test_SVD_2Cables()
        {
            // Run SVD analysis with default tolerance
            var svdResults = SVD.Solve(_structure, 1e-10);

            // Verify result is not null
            Assert.IsNotNull(svdResults);

            // Test 1: Verify rank (r)
            Assert.AreEqual(1, svdResults.r, "Rank should be 1");
            
            // Test 2: Verify static indeterminacy (s)
            Assert.AreEqual(1, svdResults.s, "Static indeterminacy should be 1");
            
            // Test 3: Verify kinematic indeterminacy (m)
            Assert.AreEqual(2, svdResults.m, "Kinematic indeterminacy should be 2");
            
            // Test 4: Verify mechanisms (inextensional modes)
            // Extract the mechanisms from Um_T
            var mechanisms = svdResults.Um_T;
            
            // Expected mechanisms: node 1 can move in y and z directions
            // The mechanisms should have zeros except for the y and z components of node 1
            // Check that the mechanisms are orthogonal to each other
            Assert.AreEqual(2, mechanisms.GetLength(0), "Um_T should have 2 rows (mechanisms) ");
            Assert.AreEqual(9, mechanisms.GetLength(1), "Um_T should have 9 columns (3*3nodes)");
            
            
            // Test 5: Verify self-stress modes
            // Extract the self-stress modes from Vs_T
            var selfStressModes = svdResults.Vs_T;
            
            // Expected result: [1,1]/sqrt(2) - both elements have equal tension
            Assert.AreEqual(1, selfStressModes.GetLength(0), "Vs_T should have 1 row (self-stress mode)");
            Assert.AreEqual(2, selfStressModes.GetLength(1), "Vs_T should have 2 columns (elements)");
            
            // Check if the self-stress mode has approximately equal values for both elements
            double expectedValue = 1.0 / Math.Sqrt(2);
            Assert.AreEqual(Math.Abs(expectedValue), Math.Abs(selfStressModes[0, 0]), 1e-10, 
                "First element in self-stress mode should have value ~0.7071");
            Assert.AreEqual(Math.Abs(expectedValue), Math.Abs(selfStressModes[0, 1]), 1e-10, 
                "Second element in self-stress mode should have value ~0.7071");
            
            // Check that the self-stress mode is normalized (sum of squares = 1)
            double sumOfSquares = selfStressModes[0, 0] * selfStressModes[0, 0] + 
                                 selfStressModes[0, 0] * selfStressModes[0, 1];
            Assert.AreEqual(1.0, sumOfSquares, 1e-10, "Self-stress mode should be normalized");
        }
    }
}
