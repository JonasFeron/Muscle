using MuscleCore.Converters;
using MuscleCore.FEModel;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Python.Runtime;
using System.IO;
using MuscleCore.PythonNETInit;

namespace MuscleCoreTests.Converters
{
    [TestClass]
    public class PyNodesConvertersTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private CoreNodes _testNodes;
        private PyNodesEncoder _encoder;
        private PyNodesDecoder _decoder;

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

            _testNodes = new CoreNodes(initialCoordinates, dof, loads, displacements);
            _encoder = new PyNodesEncoder();
            _decoder = new PyNodesDecoder();
        }


        [TestMethod]
        public void Test_Encoder_CanEncode()
        {
            // Should encode CoreNodes
            Assert.IsTrue(_encoder.CanEncode(typeof(CoreNodes)));

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
                // Should successfully encode CoreNodes
                var pyNodes = _encoder.TryEncode(_testNodes);
                Assert.IsNotNull(pyNodes);

                // Should return null for non-CoreNodes objects
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
                // Get a Python CoreNodes object
                var pyNodes = _encoder.TryEncode(_testNodes);
                Assert.IsNotNull(pyNodes);

                // Should decode to CoreNodes
                var pyType = pyNodes.GetPythonType();
                Assert.IsTrue(_decoder.CanDecode(pyType, typeof(CoreNodes)));

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
                // Get a Python CoreNodes object
                var pyNodes = _encoder.TryEncode(_testNodes);
                Assert.IsNotNull(pyNodes);

                // Should successfully decode to CoreNodes
                CoreNodes decodedNodes = null;
                var success = _decoder.TryDecode(pyNodes, out decodedNodes);
                Assert.IsTrue(success);
                Assert.IsNotNull(decodedNodes);

                // Verify properties are preserved
                Assert.AreEqual(3, decodedNodes.Count);
            }
        }
    }
}