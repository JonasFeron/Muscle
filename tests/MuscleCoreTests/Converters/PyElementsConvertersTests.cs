// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

// PythonNETGrasshopperTemplate

// Copyright <2025> <Jonas Feron>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

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
    public class PyElementsConvertersTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private static PyElementsEncoder _encoder;
        private static PyElementsDecoder _decoder;
        private static CoreElements _elements;
        private static CoreNodes _nodes;

        // private static PyObject _pythonElements;

        [ClassInitialize]
        public static void ClassInitialize(TestContext testContext)
        {
            pythonDllName = PythonNETConfig.pythonDllName;

            //         // developer mode (import musclepy from src directory)
            //         condaEnvPath = PythonNETConfig.condaEnvPath; //base environment
            //         srcDir = Path.GetFullPath(Path.Combine(
            // Directory.GetCurrentDirectory(), "..", "..", "..", "..", "..", "src","MusclePy"));

            // user mode (import musclepy from a virtual environment with a valid musclepy installation)
            condaEnvPath = @"C:\Users\Jonas\anaconda3\envs\muscledebug";
            srcDir = Path.GetFullPath(Path.Combine(
    Directory.GetCurrentDirectory(), "..", "..", "..", "..", "..", "src")); //incorrect dir

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
            _nodes = new CoreNodes(
                    new double[,] { { 0, 0, 0 }, { 1, 0, 0 }, { 0, 1, 0 } },
                    new bool[,] { { true, true, true }, { false, false, false }, { true, true, true } }
                );

                // Create test elements
            _elements = new CoreElements(
                    nodes: _nodes,
                    type: new int[] { -1, 1 },
                    endNodes: new int[,] { { 0, 1 }, { 1, 2 } },
                    area: new double[] {1000, 1000},
                    youngs: new double[,] { { 30000, 30000 }, { 0, 30000 } } // second element is a cable (0 Young's modulus in compression)
                );

            _encoder = new PyElementsEncoder();
            _decoder = new PyElementsDecoder();

        }


        [TestMethod]
        public void Test_Encoder_CanEncode()
        {
            using (Py.GIL())
            {
                // Test with valid type
                bool canEncode = _encoder.CanEncode(typeof(CoreElements));
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
                bool canDecode = _decoder.CanDecode(elementsType, typeof(CoreElements));
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
                CoreElements result = null;
                // Test with valid Python elements
                bool success = _decoder.TryDecode(pyElements, out result);
                Assert.IsTrue(success);
                Assert.IsNotNull(result);
                
                // Verify properties
                Assert.AreEqual(_elements.Type.Length, result.Type.Length);
                Assert.AreEqual(_elements.EndNodes.GetLength(0), result.EndNodes.GetLength(0));
                Assert.AreEqual(_elements.EndNodes.GetLength(1), result.EndNodes.GetLength(1));
                Assert.AreEqual(_elements.Area.GetLength(0), result.Area.GetLength(0));
                Assert.AreEqual(_elements.Youngs.GetLength(0), result.Youngs.GetLength(0));
                Assert.AreEqual(_elements.Youngs.GetLength(1), result.Youngs.GetLength(1));

            }
        }
    }
}
