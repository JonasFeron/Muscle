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

using MuscleCore.Solvers;
using MuscleCore.FEModel;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Python.Runtime;
using System.IO;
using System;
using MuscleCore.PythonNETInit;

namespace MuscleCoreTests.Solvers
{
    [TestClass]
    public class SelfStressModesTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private CoreTruss _structure;

        [TestInitialize]
        public void Initialize()
        {
            // See CoreTestsConfig.cs for more details (choose between tests in developer mode or user mode)
            PythonNETConfig testConfig = CoreTestsConfig.testConfig;
            Assert.IsTrue(testConfig.IsValid);

            PythonNETManager.Launch(testConfig);
            Assert.IsTrue(PythonNETManager.IsInitialized);
            
            // Set up the 2X Snelson structure for testing
            // Create nodes
            var nodes = new CoreNodes(
                initialCoordinates: new double[,] {
                    { 0.0, 0.0, 0.0 },   // Node 0
                    { 1.0, 0.0, -0.2 },  // Node 1
                    { 0.8, 0.0, 0.8 },   // Node 2
                    { -0.2, 0.0, 1.0 },  // Node 3
                    { 2.2, 0.0, 1.0 },   // Node 4
                    { 2.0, 0.0, 0.0 }    // Node 5
                },
                dof: new bool[,] {
                    { false, false, false },  // Node 0: fixed
                    { true, false, true },    // Node 1: free in x and z
                    { true, false, true },    // Node 2: free in x and z
                    { true, false, true },    // Node 3: free in x and z
                    { true, false, true },    // Node 4: free in x and z
                    { true, false, false }    // Node 5: free in x only
                }
            );
            // Set element properties
            double[] area = new double[11];
            for (int i = 0; i < 11; i++)
            {
                if(i==4 || i==5 || i==9 || i==10) // struts
                {
                    area[i] = 364.4;
                }
                else // cables
                {
                    area[i] = 50.3;
                }
            }


            double[,] youngsModulus = new double[11, 2];
            for (int i = 0; i < 11; i++)
            {
                youngsModulus[i, 0] = 70000; // in compression
                youngsModulus[i, 1] = 70000; // in tension
            }

            // Create elements
            var elements = new CoreElements(
                nodes: nodes,
                type: new int[] { 1, 1, 1, 1, -1, -1, 1, 1, 1, -1, -1 },  // 1 for cables, -1 for struts
                endNodes: new int[,] { 
                    { 0, 1 },  // Element 0
                    { 1, 2 },  // Element 1
                    { 2, 3 },  // Element 2
                    { 0, 3 },  // Element 3
                    { 0, 2 },  // Element 4 - strut
                    { 1, 3 },  // Element 5 - strut
                    { 2, 4 },  // Element 6
                    { 4, 5 },  // Element 7
                    { 1, 5 },  // Element 8
                    { 1, 4 },  // Element 9 - strut
                    { 2, 5 }   // Element 10 - strut
                },
                area: area,
                youngs: youngsModulus
            );



            // Create structure
            _structure = new CoreTruss(nodes, elements);
        }

        [TestCleanup]
        public void Cleanup()
        {
            PythonNETManager.ShutDown();
        }

        [TestMethod]
        public void Test_LocalizeSelfStressModes_2XSnelson()
        {
            // First, run SVD analysis to get the self-stress modes
            var svdResults = SVD.Solve(_structure, 1e-10);

            // Verify result is not null
            Assert.IsNotNull(svdResults);
            
            // Verify we have 2 self-stress modes (s=2)
            Assert.AreEqual(2, svdResults.s, "Static indeterminacy should be 2");
            
            // Get the self-stress modes
            var selfStressModes = svdResults.Vs_T;
            
            // Now localize the self-stress modes
            double[,] localizedModes = SelfStressModes.Localize(_structure, selfStressModes, 1e-6);
            
            // Verify result is not null
            Assert.IsNotNull(localizedModes);
            
            // Verify dimensions
            Assert.AreEqual(2, localizedModes.GetLength(0), "Should have 2 localized modes");
            Assert.AreEqual(11, localizedModes.GetLength(1), "Each mode should have 11 components (one per element)");
            
            // Expected localized modes based on the Python test
            double[,] expectedLocalizedModes = new double[,] {
                { 0.60, 0.60, 0.60, 0.60, -0.67, -1.00, 0.00, 0.00, 0.00, 0.00, 0.00 },
                { 0.00, 0.56, 0.00, 0.00, 0.00, 0.00, 0.59, 0.64, 0.83, -1.00, -0.83 }
            };
            
            // Compare the absolute values of the localized modes with the expected values
            // We use absolute values because the sign of the modes can be flipped
            for (int i = 0; i < 2; i++)
            {
                for (int j = 0; j < 11; j++)
                {
                    Assert.AreEqual(
                        expectedLocalizedModes[i, j], 
                        localizedModes[i, j], 
                        0.01, 
                        $"Mode {i}, Element {j}: Expected {expectedLocalizedModes[i, j]}, Got {localizedModes[i, j]}"
                    );
                }
            }
        }
    }
}
