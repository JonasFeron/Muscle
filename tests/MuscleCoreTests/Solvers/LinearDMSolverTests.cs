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
    public class LinearDMSolverTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;


        [TestInitialize]
        public void Initialize()
        {
            condaEnvPath = PythonNETConfig.condaEnvPath;
            pythonDllName = PythonNETConfig.pythonDllName;


            srcDir = Path.GetFullPath(Path.Combine(Directory.GetCurrentDirectory(),
             "..", "..", "..", "..", "..", "src"));


            PythonNETManager.Initialize(condaEnvPath, pythonDllName, srcDir);
        }

        [TestCleanup]
        public void Cleanup()
        {
            PythonNETManager.ShutDown();
        }

        [TestMethod]
        public void Test_LinearDMSolver()
        {
            // Create nodes
            var nodes = new CoreNodes(
                initialCoordinates: new double[,] {
                    { 0.0, 0.0, 0.0 },  // Node 0: origin
                    { 1.0, 0.0, 1.0 },  // Node 1: top
                    { 2.0, 0.0, 0.0 }   // Node 2: right
                },
                dof: new bool[,] {
                    { false, false, false },  // Node 0: fixed
                    { true, false, true },    // Node 1: free in x,z
                    { false, false, false }   // Node 2: fixed
                }
            );

            // Create elements
            var elements = new CoreElements(
                nodes: nodes,
                type: new int[] { -1, -1 },  // Two struts
                endNodes: new int[,] { { 0, 1 }, { 1, 2 } },  // Element 0: 0->1, Element 1: 1->2
                area: new double[] { 2500.0, 2500.0 },   // 2500 mm² area
                youngs: new double[,] { { 10000.0, 10000.0 }, { 10000.0, 10000.0 } },  // 10000 MPa Young's modulus
                freeLength: new double[] { Math.Sqrt(2), Math.Sqrt(2) }  // Initial free length matching the initial geometry
            );

            // Create structure
            var structure = new CoreTruss(nodes, elements);

            // Apply -100kN vertical load at node 1
            var loads = new double[9];  // 3 nodes * 3 DOFs
            loads[5] = -100000.0;  // Node 1, Z direction

            // No prestress
            var deltaFreeLength = new double[2];  // 2 elements

            // Solve using LinearDM
            var result = LinearDM.Solve(structure, loads, deltaFreeLength);

            // Verify result is not null
            Assert.IsNotNull(result);

            // Check displacements
            var d1z = result.Nodes.Displacements[1, 2];  // Node 1, Z displacement
            Assert.AreEqual(-5.6568e-3, d1z, 1e-6);

            // Check tensions (analytical solution)
            var analyticTension = -100000.0 / Math.Sqrt(2);  // -70711.0 N
            Assert.AreEqual(analyticTension, result.Elements.Tension[0], 1e-1);
            Assert.AreEqual(analyticTension, result.Elements.Tension[1], 1e-1);

            // Check reactions (analytical solution)
            var reactions = result.Nodes.Reactions;
            Assert.AreEqual(50000.0, reactions[0, 0], 1e-1);  // Node 0 X
            Assert.AreEqual(0.0, reactions[0, 1], 1e-1);      // Node 0 Y
            Assert.AreEqual(50000.0, reactions[0, 2], 1e-1);  // Node 0 Z
            Assert.AreEqual(0.0, reactions[1, 0], 1e-1);      // Node 1 X (free)
            Assert.AreEqual(0.0, reactions[1, 1], 1e-1);      // Node 1 Y
            Assert.AreEqual(0.0, reactions[1, 2], 1e-1);      // Node 1 Z (free)
            Assert.AreEqual(-50000.0, reactions[2, 0], 1e-1); // Node 2 X
            Assert.AreEqual(0.0, reactions[2, 1], 1e-1);      // Node 2 Y
            Assert.AreEqual(50000.0, reactions[2, 2], 1e-1);  // Node 2 Z

            // Check resisting forces
            var resistingForces = result.Nodes.ResistingForces;
            Assert.AreEqual(50000.0, resistingForces[0, 0], 1e-1);   // Node 0 X
            Assert.AreEqual(0.0, resistingForces[0, 1], 1e-1);       // Node 0 Y
            Assert.AreEqual(50000.0, resistingForces[0, 2], 1e-1);   // Node 0 Z
            Assert.AreEqual(0.0, resistingForces[1, 0], 1e-1);       // Node 1 X
            Assert.AreEqual(0.0, resistingForces[1, 1], 1e-1);       // Node 1 Y
            Assert.AreEqual(-100000.0, resistingForces[1, 2], 1e-1); // Node 1 Z
            Assert.AreEqual(-50000.0, resistingForces[2, 0], 1e-1);  // Node 2 X
            Assert.AreEqual(0.0, resistingForces[2, 1], 1e-1);       // Node 2 Y
            Assert.AreEqual(50000.0, resistingForces[2, 2], 1e-1);   // Node 2 Z

            // Check equilibrium
            Assert.IsTrue(result.IsInEquilibrium);
        }
    }
}
