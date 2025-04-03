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
    public class DRSolverTests
    {

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
        public void Test_2CablesLoading()
        {
            // Create nodes based on the Python test
            var nodes = new CoreNodes(
                initialCoordinates: new double[,] {
                    { -2.0, 0.0, 0.0 },  // Node 0: left support
                    { 0.0, 0.0, 0.0 },   // Node 1: free to move
                    { 2.0, 0.0, 0.0 }    // Node 2: right support
                },
                dof: new bool[,] {
                    { false, false, false },  // Node 0: fixed
                    { true, false, true },    // Node 1: free in x,z
                    { false, false, false }   // Node 2: fixed
                }
            );

            // Create elements with the same properties as in the Python test
            double cableArea = Math.PI * Math.Pow(8.0 / 2.0, 2);  // 8mm diameter cable area in mm²
            var elements = new CoreElements(
                nodes: nodes,
                type: new int[] { 1, 1 },  // Two cables
                endNodes: new int[,] { { 0, 1 }, { 1, 2 } },  // Element 0: 0->1, Element 1: 1->2
                area: new double[] { cableArea, cableArea },  // 50.26 mm² area
                youngs: new double[,] { { 70000.0, 70000.0 }, { 70000.0, 70000.0 } }  // 70000 MPa Young's modulus
            );

            // Create structure
            var structure = new CoreTruss(nodes, elements);

            // Configure solver with the same parameters as in the Python test
            var config = new CoreConfigDR(
                dt: 0.01,
                massAmplFactor: 1.0,
                minMass: 0.005,
                maxTimeStep: 100,
                maxKEResets: 20,
                zeroResidualRTol: 1e-6,
                zeroResidualATol: 1e-6
            );

            // No prestress
            var deltaFreeLength = new double[2] { 0.0, 0.0 };

            // External loads - vertical load at Node 1
            var loads = new double[9];  // 3 nodes * 3 DOFs
            loads[5] = 888.808;  // Node 1, Z direction (888.808 N)

            // Solve using Dynamic Relaxation
            var result = DynamicRelaxation.Solve(structure, loads, deltaFreeLength, config);

            // Verify result is not null
            Assert.IsNotNull(result);

            // Verify the solver converged updated the resulting number of time steps and resets
            Assert.IsTrue(config.NTimeStep > 0);
            Assert.IsTrue(config.NKEReset > 0);

            // Verify the solver converged within the maximum number of steps
            Assert.IsTrue(config.NTimeStep < config.MaxTimeStep);
            Assert.IsTrue(config.NKEReset < config.MaxKEResets);

            // Check resisting forces
            double expectedResistingForce = 888.808; // N
            Assert.AreEqual(expectedResistingForce, result.Nodes.ResistingForces[1, 2], 0.001);

            // Check vertical reactions
            double expectedVerticalReaction = -444.404; // N
            Assert.AreEqual(expectedVerticalReaction, result.Nodes.Reactions[0, 2], 0.001);
            Assert.AreEqual(expectedVerticalReaction, result.Nodes.Reactions[2, 2], 0.001);

            // Check tensions
            double expectedTension = 7037.17; // N
            Assert.AreEqual(expectedTension, result.Elements.Tension[0], 0.01);
            Assert.AreEqual(expectedTension, result.Elements.Tension[1], 0.01);

            // Check final node position
            double expectedNode1Z = 0.126554; // m
            Assert.AreEqual(expectedNode1Z, result.Nodes.Coordinates[1, 2], 1e-6);

            // Check equilibrium
            Assert.IsTrue(result.IsInEquilibrium);
        }
    }
}
