using MuscleCore.Application.PythonNETSolvers;
using MuscleCore.Converters;
using MuscleCore.FEModel;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Python.Runtime;
using System.IO;
using MuscleCore.PythonNETInit;

namespace MuscleCoreTests.Converters
{
    [TestClass]
    public class FEM_NodesInitializerTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private FEM_Nodes _testNodes;
        private FEM_NodesEncoder _encoder;
        private FEM_NodesDecoder _decoder;

        [ClassInitialize]
        public static void ClassInitialize(TestContext testContext)
        {
            condaEnvPath = PythonNETConfig.condaEnvPath;
            pythonDllName = PythonNETConfig.pythonDllName;

            srcDir = Path.GetFullPath(Path.Combine(
            Directory.GetCurrentDirectory(), "..", "..", "..", "..", "..", "src"));

            PythonNETManager.Initialize(condaEnvPath, pythonDllName, srcDir);

        }

        [ClassCleanup]
        public static void ClassCleanup()
        {
            PythonNETManager.ShutDown();
        }

        [TestInitialize]
        public void SetUp()
        {
            var initialCoordinates = new double[,]
            {
                { 0.0, 0.0, 0.0 },  // Node 0: origin
                { 1.0, 0.0, 1.0 },  // Node 1: top
                { 2.0, 0.0, 0.0 }   // Node 2: right
            };
            
            var dof = new bool[,]
            {
                { false, false, false },  // Node 0: fixed
                { true, false, true },    // Node 1: free in x,z
                { false, false, false }   // Node 2: fixed
            };

            var loads = new double[,]
            {
                { 0.0, 0.0, 0.0 },
                { 100.0, 0.0, -50.0 },
                { 0.0, 0.0, 0.0 }
            };

            var displacements = new double[,]
            {
                { 0.0, 0.0, 0.0 },  // Node 0: origin
                { 0.1, 0.0, -0.2 },  // Node 1: top
                { 0.0, 0.0, 0.0 }   // Node 2: right
            };

            _testNodes = new FEM_Nodes(initialCoordinates, dof, loads, displacements);
            _encoder = new FEM_NodesEncoder();
            _decoder = new FEM_NodesDecoder();
        }

        [TestMethod]
        public void Test_FEM_NodesInitializer()
        {
            // Initialize nodes using FEM_NodesInitializer
            var initializedNodes = FEM_NodesInitializer.Initialize(_testNodes);
            Assert.IsNotNull(initializedNodes);

            // Check that all properties are properly initialized
            Assert.AreEqual(3, initializedNodes.Count);
            Assert.AreEqual(7, initializedNodes.FixationsCount); // 2 fixed nodes (6 DOFs) + 1 fixed Y DOF

            // Check arrays have correct dimensions
            Assert.AreEqual(3, initializedNodes.Coordinates.GetLength(0));
            Assert.AreEqual(3, initializedNodes.Coordinates.GetLength(1));

            // Check coordinates = initial_coordinates + displacements
            for (int i = 0; i < initializedNodes.Count; i++)
            {
                for (int j = 0; j < 3; j++)
                {
                    Assert.AreEqual(
                        initializedNodes.Coordinates[i,j], 
                        initializedNodes.InitialCoordinates[i,j] + initializedNodes.Displacements[i,j]
                    );
                }
            }

            // Check residual = loads + reactions - resisting_forces
            for (int i = 0; i < initializedNodes.Count; i++)
            {
                for (int j = 0; j < 3; j++)
                {
                    Assert.AreEqual(
                        initializedNodes.Residuals[i,j], 
                        initializedNodes.Loads[i,j] + initializedNodes.Reactions[i,j] - initializedNodes.ResistingForces[i,j]
                    );
                }
            }

            // Check specific values
            // Node 1 (middle) should have non-zero loads
            Assert.AreEqual(100.0, initializedNodes.Loads[1,0]); // X load
            Assert.AreEqual(-50.0, initializedNodes.Loads[1,2]); // Z load
        }

        [TestMethod]
        public void Test_Encoder_CanEncode()
        {
            // Should encode FEM_Nodes
            Assert.IsTrue(_encoder.CanEncode(typeof(FEM_Nodes)));

            // Should not encode other types
            Assert.IsFalse(_encoder.CanEncode(typeof(string)));
            Assert.IsFalse(_encoder.CanEncode(typeof(int)));
            Assert.IsFalse(_encoder.CanEncode(typeof(object)));
        }

        [TestMethod]
        public void Test_Encoder_TryEncode()
        {
            using (Py.GIL())
            {
                // Should successfully encode FEM_Nodes
                var pyNodes = _encoder.TryEncode(_testNodes);
                Assert.IsNotNull(pyNodes);

                // Should return null for non-FEM_Nodes objects
                Assert.IsNull(_encoder.TryEncode("not a node"));
                Assert.IsNull(_encoder.TryEncode(42));
                Assert.IsNull(_encoder.TryEncode(new object()));
            }
        }

        [TestMethod]
        public void Test_Decoder_CanDecode()
        {
            using (Py.GIL())
            {
                // Get a Python FEM_Nodes object
                var pyNodes = _encoder.TryEncode(_testNodes);
                Assert.IsNotNull(pyNodes);

                // Should decode to FEM_Nodes
                var pyType = pyNodes.GetPythonType();
                Assert.IsTrue(_decoder.CanDecode(pyType, typeof(FEM_Nodes)));

                // Should not decode to other types
                Assert.IsFalse(_decoder.CanDecode(pyType, typeof(string)));
                Assert.IsFalse(_decoder.CanDecode(pyType, typeof(int)));
                Assert.IsFalse(_decoder.CanDecode(pyType, typeof(object)));
            }
        }

        [TestMethod]
        public void Test_Decoder_TryDecode()
        {
            using (Py.GIL())
            {
                // Get a Python FEM_Nodes object
                var pyNodes = _encoder.TryEncode(_testNodes);
                Assert.IsNotNull(pyNodes);

                // Should successfully decode to FEM_Nodes
                FEM_Nodes decodedNodes = null;
                var success = _decoder.TryDecode(pyNodes, out decodedNodes);
                Assert.IsTrue(success);
                Assert.IsNotNull(decodedNodes);

                // Verify properties are preserved
                Assert.AreEqual(3, decodedNodes.Count);
                Assert.AreEqual(7, decodedNodes.FixationsCount);

                //// Should fail to decode to other types
                //Assert.IsFalse(_decoder.TryDecode(pyNodes, out string? _));
                //Assert.IsFalse(_decoder.TryDecode(pyNodes, out int? _));
                //Assert.IsFalse(_decoder.TryDecode(pyNodes, out object? _));
            }
        }
    }
}