using Microsoft.VisualStudio.TestTools.UnitTesting;
using MuscleCore.Solvers;
using MuscleCore.Converters;
using MuscleCore.FEModel;
using Python.Runtime;
using System.IO;
using MuscleCore.PythonNETInit;

namespace MuscleCoreTests.Converters
{
    [TestClass]
    public class FEM_StructureInitializerTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private static FEM_StructureEncoder _encoder;
        private static FEM_StructureDecoder _decoder;
        private static FEM_Elements _elements;
        private static FEM_Nodes _nodes;
        private static FEM_Structure _structure;

        // private static PyObject _pythonElements;

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
            _nodes = new FEM_Nodes(
                    new double[,] { { 0, 0, 0 }, { 1, 0, 0 }, { 0, 1, 0 } },
                    new bool[,] { { true, true, true }, { false, false, false }, { true, true, true } },
                    loads: new double[,] { { 0, 0, 0 }, { 100, 0, -50 }, { 0, 0, 0 } }
                );

                // Create test elements
            _elements = new FEM_Elements(
                    nodes: _nodes,
                    type: new int[] { -1, 1 },
                    endNodes: new int[,] { { 0, 1 }, { 1, 2 } },
                    area: new double[] { 1000, 1000 },
                    youngs: new double[,] { { 30000, 30000 }, { 0, 30000 } } // second element is a cable (0 Young's modulus in compression)
                );

            _structure = new FEM_Structure(
                nodes: _nodes,
                elements: _elements
            );
            _encoder = new FEM_StructureEncoder();
            _decoder = new FEM_StructureDecoder();

        }


        [TestMethod]
        public void Test_Encoder_CanEncode()
        {
            using (Py.GIL())
            {
                // Test with valid type
                bool canEncode = _encoder.CanEncode(typeof(FEM_Structure));
                Assert.IsTrue(canEncode);

                // Test with invalid type
                canEncode = _encoder.CanEncode(typeof(string));
                Assert.IsFalse(canEncode);
            }
        }

        [TestMethod]
        public void Test_Encoder_TryEncode()
        {
            using (Py.GIL())
            {
                PyObject result = _encoder.TryEncode(_structure);
                // Test with valid elements
                Assert.IsNotNull(result);

                // Test with invalid elements
                Assert.IsNull(_encoder.TryEncode(new object()));

            }
        }

        [TestMethod]
        public void Test_Decoder_CanDecode()
        {
            using (Py.GIL())
            {
                PyObject pyStructure = _structure.ToPython();

                // Get Python type
                PyType structureType = pyStructure.GetPythonType();

                // Test with valid type
                bool canDecode = _decoder.CanDecode(structureType, typeof(FEM_Structure));
                Assert.IsTrue(canDecode);

                // Test with invalid target type
                canDecode = _decoder.CanDecode(structureType, typeof(string));
                Assert.IsFalse(canDecode);

            }
        }

        [TestMethod]
        public void Test_Decoder_TryDecode()
        {
            using (Py.GIL())
            {
                PyObject pyStructure =_structure.ToPython();
                FEM_Structure result = null;
                // Test with valid Python elements
                bool success = _decoder.TryDecode(pyStructure, out result);
                Assert.IsTrue(success);
                Assert.IsNotNull(result);
                Assert.IsFalse(result.IsInEquilibrium); //there are loads on the nodes without axial forces in the elements

            }
        }
    }
}
