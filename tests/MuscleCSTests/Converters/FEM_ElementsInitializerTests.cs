using Microsoft.VisualStudio.TestTools.UnitTesting;
using MuscleCore.Application.PythonNETSolvers;
using MuscleCore.Converters;
using MuscleCore.FEModel;
using Python.Runtime;
using System.IO;
using MuscleCore.App.PythonNETInit;

namespace MuscleCSTests.Converters
{
    [TestClass]
    public class FEM_ElementsInitializerTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private static FEM_ElementsEncoder _encoder;
        private static FEM_ElementsDecoder _decoder;
        private static FEM_Elements _elements;
        private static FEM_Nodes _nodes;

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
                    new bool[,] { { true, true, true }, { false, false, false }, { true, true, true } }
                );

                // Create test elements
            _elements = new FEM_Elements(
                    nodes: _nodes,
                    type: new int[] { -1, 1 },
                    endNodes: new int[,] { { 0, 1 }, { 1, 2 } },
                    areas: new double[,] { { 1000, 1000 }, { 1000, 1000 } },
                    youngs: new double[,] { { 30000, 30000 }, { 0, 30000 } } // second element is a cable (0 Young's modulus in compression)
                );

            _encoder = new FEM_ElementsEncoder();
            _decoder = new FEM_ElementsDecoder();

        }


        [TestMethod]
        public void Test_Encoder_CanEncode()
        {
            using (Py.GIL())
            {
                // Test with valid type
                bool canEncode = _encoder.CanEncode(typeof(FEM_Elements));
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
                PyObject result = _encoder.TryEncode(_elements);
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
                PyObject pyElements = _elements.ToPython();

                // Get Python type
                PyType elementsType = pyElements.GetPythonType();

                // Test with valid type
                bool canDecode = _decoder.CanDecode(elementsType, typeof(FEM_Elements));
                Assert.IsTrue(canDecode);

                // Test with invalid target type
                canDecode = _decoder.CanDecode(elementsType, typeof(string));
                Assert.IsFalse(canDecode);

            }
        }

        [TestMethod]
        public void Test_Decoder_TryDecode()
        {
            using (Py.GIL())
            {
                PyObject pyElements =_elements.ToPython();
                FEM_Elements result = null;
                // Test with valid Python elements
                bool success = _decoder.TryDecode(pyElements, out result);
                Assert.IsTrue(success);
                Assert.IsNotNull(result);
                
                // Verify properties
                Assert.AreEqual(_elements.Type.Length, result.Type.Length);
                Assert.AreEqual(_elements.EndNodes.GetLength(0), result.EndNodes.GetLength(0));
                Assert.AreEqual(_elements.EndNodes.GetLength(1), result.EndNodes.GetLength(1));
                Assert.AreEqual(_elements.Areas.GetLength(0), result.Areas.GetLength(0));
                Assert.AreEqual(_elements.Areas.GetLength(1), result.Areas.GetLength(1));
                Assert.AreEqual(_elements.Youngs.GetLength(0), result.Youngs.GetLength(0));
                Assert.AreEqual(_elements.Youngs.GetLength(1), result.Youngs.GetLength(1));

            }
        }
    }
}
