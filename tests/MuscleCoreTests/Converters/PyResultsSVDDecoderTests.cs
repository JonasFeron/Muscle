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

using MuscleCore.Converters;
using MuscleCore.Solvers;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Python.Runtime;
using System.IO;
using MuscleCore.PythonNETInit;

namespace MuscleCoreTests.Converters
{
    [TestClass]
    public class PyResultsSVDDecoderTests
    {

        private PyResultsSVDDecoder _decoder;
        private dynamic _pyResultsSVD;

        [ClassInitialize]
        public static void ClassInitialize(TestContext testContext)
        {
            // See CoreTestsConfig.cs for more details (choose between tests in developer mode or user mode)
            PythonNETConfig testConfig = CoreTestsConfig.testConfig;
            Assert.IsTrue(testConfig.IsValid);

            PythonNETManager.Launch(testConfig);
            Assert.IsTrue(PythonNETManager.IsInitialized);
        }

        [ClassCleanup]
        public static void ClassCleanup()
        {
            PythonNETManager.ShutDown();
        }

        [TestInitialize]
        public void SetUp()
        {
            using (Py.GIL())
            {
                // Create a Python PyResultsSVD object
                dynamic np = Py.Import("numpy");
                dynamic musclepy = Py.Import("musclepy");
                dynamic PyResultsSVD = musclepy.PyResultsSVD; // import the python PyResultsSVD class
                // Create test data for PyResultsSVD
                int r = 2;
                int s = 1;
                int m = 3;
                
                // Create numpy arrays for the SVD components
                dynamic Ur = np.array(new double[,] { { 1.0, 0.0 }, { 0.0, 1.0 }, { 0.5, 0.5 } }); // 3 rows, 2 columns
                dynamic Um = np.array(new double[,] { { 0.1, 0.2, 0.3 }, { 0.4, 0.5, 0.6 }, { 0.7, 0.8, 0.9 } });
                dynamic Sr = np.array(new double[] { 10.0, 5.0 });
                dynamic Vr = np.array(new double[,] { { 0.8, 0.6 }, { 0.6, -0.8 } });
                dynamic Vs = np.array(new double[,] { { 0.7 }, { 0.7 } });
                
                // Create PyResultsSVD Python object
                _pyResultsSVD = PyResultsSVD(r, s, m, Ur, Um, Sr, Vr, Vs);
            }

            _decoder = new PyResultsSVDDecoder();
        }

        [TestMethod]
        public void Test_Decoder_CanDecode()
        {
            using (Py.GIL())
            {
                // Get Python type
                var pyType = ((PyObject)_pyResultsSVD).GetPythonType();
                
                // Should decode to CoreResultsSVD
                Assert.IsTrue(_decoder.CanDecode(pyType, typeof(CoreResultsSVD)));
                
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
                // Should successfully decode to CoreResultsSVD
                CoreResultsSVD decodedResults = null;
                var success = _decoder.TryDecode((PyObject)_pyResultsSVD, out decodedResults);
                Assert.IsTrue(success);
                Assert.IsNotNull(decodedResults);
                
                // Verify properties are preserved
                Assert.AreEqual(2, decodedResults.r);
                Assert.AreEqual(1, decodedResults.s);
                Assert.AreEqual(3, decodedResults.m);
                
                // Verify array dimensions
                Assert.AreEqual(2, decodedResults.Ur_T.GetLength(0)); // 2 rows (transposed from 2 columns)
                Assert.AreEqual(3, decodedResults.Ur_T.GetLength(1)); // 3 columns (transposed from 3 rows)
                
                Assert.AreEqual(3, decodedResults.Um_T.GetLength(0)); // 3 rows 
                Assert.AreEqual(3, decodedResults.Um_T.GetLength(1)); // 3 columns 
                
                Assert.AreEqual(2, decodedResults.Sr.Length); // 2 singular values
                
                Assert.AreEqual(2, decodedResults.Vr_T.GetLength(0)); // 2 rows 
                Assert.AreEqual(2, decodedResults.Vr_T.GetLength(1)); // 2 columns
                
                Assert.AreEqual(1, decodedResults.Vs_T.GetLength(0)); // 1 row (transposed from 1 column)
                Assert.AreEqual(2, decodedResults.Vs_T.GetLength(1)); // 2 columns (transposed from 2 rows)
                
                // Verify some values
                Assert.AreEqual(10.0, decodedResults.Sr[0], 1e-10);
                Assert.AreEqual(5.0, decodedResults.Sr[1], 1e-10);
            }
        }

        [TestMethod]
        public void Test_Decoder_TryDecode_InvalidType()
        {
            using (Py.GIL())
            {
                // Create a Python object that is not a PyResultsSVD
                dynamic np = Py.Import("numpy");
                dynamic array = np.array(new double[] { 1.0, 2.0, 3.0 });
                
                // Should not decode to CoreResultsSVD
                CoreResultsSVD decodedResults = null;
                var success = _decoder.TryDecode((PyObject)array, out decodedResults);
                Assert.IsFalse(success);
                Assert.IsNull(decodedResults);
            }
        }
    }
}
