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
    public class PyConfigDRConvertersTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private CoreConfigDR _testConfig;
        private PyConfigDREncoder _encoder;

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
            // Create a test configuration with non-default values
            _testConfig = new CoreConfigDR(
                dt: 0.02,
                massAmplFactor: 2.0,
                minMass: 0.01,
                maxTimeStep: 5000,
                maxKEResets: 500,
                zeroResidualRTol: 1e-5,
                zeroResidualATol: 1e-7
            );
            
            _encoder = new PyConfigDREncoder();
        }

        [TestMethod]
        public void Test_Encoder_CanEncode()
        {
            // Should encode CoreConfigDR
            Assert.IsTrue(_encoder.CanEncode(typeof(CoreConfigDR)));

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
                // Should successfully encode CoreConfigDR
                var pyConfig = _encoder.TryEncode(_testConfig);
                Assert.IsNotNull(pyConfig);

                // Should return null for non-CoreConfigDR objects
                Assert.IsNull(_encoder.TryEncode("not a config"));
                Assert.IsNull(_encoder.TryEncode(42));
                Assert.IsNull(_encoder.TryEncode(new object()));
            }
        }
    }
}
