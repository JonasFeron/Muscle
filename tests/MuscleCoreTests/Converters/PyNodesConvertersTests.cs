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