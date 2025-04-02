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
using System.IO;
using MuscleCore.PythonNETInit;
using MuscleCore.Solvers;

namespace MuscleCoreTests.Solvers
{
    [TestClass]
    public class TestScriptSolverTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;


        [TestInitialize]
        public void Initialize()
        {
            // See CoreTestsConfig.cs for more details (choose between tests in developer mode or user mode)
            PythonNETConfig testConfig = CoreTestsConfig.testConfig;
            Assert.IsTrue(testConfig.IsValid);

            PythonNETManager.Launch(testConfig);
            Assert.IsTrue(PythonNETManager.IsInitialized);
        }

        [TestCleanup]
        public void Cleanup()
        {
            PythonNETManager.ShutDown();
        }



        [TestMethod]
        public void TestHelloFromPython()
        {
            // Arrange
            string str0 = "HELLO";
            string str1 = "from python";

            // Act
            string result = TestScriptSolver.Solve(str0, str1);

            // Assert
            Assert.IsNotNull(result);
            Assert.AreEqual("hello FROM PYTHON", result);
        }
    }
}
