using MuscleCore.Solvers;
using MuscleCore.FEModel;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Python.Runtime;
using System.IO;
using System;
using MuscleCore.PythonNETInit;
using System.Linq;

namespace MuscleCoreTests.Solvers
{
    [TestClass]
    public class DynamicModalAnalysisTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private CoreTruss _formFoundStructure;
        private double[] _pointMasses;
        private double[] _elementMasses;

        [TestInitialize]
        public void Initialize()
        {
            condaEnvPath = PythonNETConfig.condaEnvPath;
            pythonDllName = PythonNETConfig.pythonDllName;

            srcDir = Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(),
             "..", "..", "..", "..", "..", "src"));

            PythonNETManager.Initialize(condaEnvPath, pythonDllName, srcDir);
            
            // Set up the experimental simplex structure for testing
            SetupSimplexStructure();
        }

        private void SetupSimplexStructure()
        {
            // Create nodes with coordinates in meters
            double[,] coordinates = new double[,]
            {
                { 0.00, -2.0438, 0.00 },     // Node 0
                { 0.00, 0.00, 0.00 },        // Node 1
                { 1.770, -1.0219, 0.00 },    // Node 2
                { 0.590, -2.2019, 1.950 },   // Node 3
                { -0.4319, -0.4319, 1.950 }, // Node 4
                { 1.6119, -0.4319, 1.950 }   // Node 5
            };
            
            // Define DOF (true = free, false = fixed)
            bool[,] dof = new bool[,]
            {
                { false, true, false },    // Node 0
                { false, false, false },   // Node 1
                { true, true, false },     // Node 2
                { true, true, true },      // Node 3
                { true, true, true },      // Node 4
                { true, true, true }       // Node 5
            };
            
            var nodes = new CoreNodes(coordinates, dof);
            
            // Create elements
            int[,] endNodes = new int[,]
            {
                { 2, 4 },   // Element 0
                { 1, 3 },   // Element 1
                { 0, 5 },   // Element 2
                { 1, 2 },   // Element 3
                { 0, 1 },   // Element 4
                { 0, 2 },   // Element 5
                { 4, 5 },   // Element 6
                { 3, 4 },   // Element 7
                { 3, 5 },   // Element 8
                { 2, 5 },   // Element 9
                { 1, 4 },   // Element 10
                { 0, 3 }    // Element 11
            };
            
            // Set element types (1 for cables, -1 for struts)
            int[] elementsType = Enumerable.Repeat(1, 12).ToArray();
            elementsType[0] = -1;
            elementsType[1] = -1;
            elementsType[2] = -1;
            
            // Set Young moduli [in compression, in tension] MPa
            double[,] elementsE = new double[12, 2];
            // Struts (can only be in compression)
            for (int i = 0; i < 3; i++)
            {
                elementsE[i, 0] = 70390;
                elementsE[i, 1] = 0;
            }
            // Cables (can only be in tension)
            for (int i = 3; i < 9; i++)
            {
                elementsE[i, 0] = 0;
                elementsE[i, 1] = 71750;
            }
            for (int i = 9; i < 12; i++)
            {
                elementsE[i, 0] = 0;
                elementsE[i, 1] = 72190;
            }
            
            // Set cross-sectional areas [mm²]
            double[] elementsA = new double[12];
            for (int i = 0; i < 3; i++)
            {
                elementsA[i] = 364.4; // struts
            }
            for (int i = 3; i < 12; i++)
            {
                elementsA[i] = 50.3; // cables
            }
            
            var elements = new CoreElements(nodes, elementsType, endNodes, elementsA , elementsE);
            
            // Create CoreTruss
            var structure = new CoreTruss(nodes, elements);


            // Configure solver for form-finding
            var config = new CoreConfigDR(
                dt: 0.01,
                massAmplFactor: 1.0,
                minMass: 0.005,
                maxTimeStep: 1000,
                maxKEResets: 100,
                zeroResidualRTol: 1e-4,
                zeroResidualATol: 1e-6
            );

            
            // Set free length variation for initial self-stress level = 1.5kN
            double[] freeLengthVariation = new double[12];
            for (int i = 0; i < 3; i++)
            {
                freeLengthVariation[i] = 0.000717; // [m] struts
            }
            


            // Set self-weight (including element weight)
            double[] selfWeight = new double[18];
            selfWeight[2] = -45.7; // Node 0 Z
            selfWeight[5] = -45.7; // Node 1 Z
            selfWeight[8] = -45.7; // Node 2 Z
            selfWeight[11] = -50.3; // Node 3 Z
            selfWeight[14] = -50.3; // Node 4 Z
            selfWeight[17] = -50.3; // Node 5 Z
            
            
            // Point mass (nodes only)(active in the 3 directions)
            _pointMasses = new double[18]; // 6 nodes * 3 directions
            for (int i = 0; i < 3; i++) // Bottom nodes
            {
                for (int j = 0; j < 3; j++) // X, Y, Z directions
                {
                    _pointMasses[i * 3 + j] = 2.642; // kg
                }
            }
            for (int i = 3; i < 6; i++) // Top nodes
            {
                for (int j = 0; j < 3; j++) // X, Y, Z directions
                {
                    _pointMasses[i * 3 + j] = 3.06; // kg, including loading plate
                }
            }
            
            // Element mass (elements only)
            _elementMasses = new double[12];
            for (int i = 0; i < 3; i++)
            {
                _elementMasses[i] = 2.63; // kg, struts, including accelerometer
            }
            for (int i = 3; i < 12; i++)
            {
                _elementMasses[i] = 0.502; // kg, cables
            }
            

            _formFoundStructure = DynamicRelaxation.Solve(structure, selfWeight, freeLengthVariation, config);

        }

        [TestCleanup]
        public void Cleanup()
        {
            PythonNETManager.ShutDown();
        }

        [TestMethod]
        public void Test_ConsistentMassMatrix()
        {
            // Verify form-finding results - axial force in struts should be around -1.5kN
            double avgStrutForce = 0;
            for (int i = 0; i < 3; i++)
            {
                avgStrutForce += _formFoundStructure.Elements.Tension[i];
            }
            avgStrutForce /= 3;
            
            Assert.AreEqual(-1500, avgStrutForce, 1, "Average axial force in struts should be -1.5kN");
            
            // Run dynamic modal analysis with consistent mass matrix (option 2)
            var dynamicResults = DynamicModalAnalysis.Solve(
                _formFoundStructure,
                _pointMasses,
                _elementMasses,
                elementMassesOption: 2, // consistent mass matrix
                nModes: 0 // compute all modes
            );
            
            // Verify result is not null
            Assert.IsNotNull(dynamicResults, "Dynamic analysis results should not be null");
            
            // Check masses
            Assert.AreEqual(18, dynamicResults.Masses.Length, "Masses array should have 18 elements (6 nodes * 3 directions)");
            
            
            // Check number of modes
            Assert.AreEqual(12, dynamicResults.ModeCount, "Should compute 12 natural modes");
            
            // Check mode shapes dimensions
            Assert.AreEqual(12, dynamicResults.ModeShapes.GetLength(0), "Mode shapes should have 12 rows (modes)");
            Assert.AreEqual(18, dynamicResults.ModeShapes.GetLength(1), "Mode shapes should have 18 columns (6 nodes * 3 directions)");
            
            
            // Check natural frequency
            Assert.AreEqual(2.346, dynamicResults.Frequencies[0], 0.001, "First natural frequency should be approximately 2.346 Hz");
        }
    }
}
