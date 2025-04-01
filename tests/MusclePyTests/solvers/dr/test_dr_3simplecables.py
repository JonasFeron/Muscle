# Muscle

# Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# List of the contributors to the development of Muscle: see NOTICE file.
# Description and complete License: see NOTICE file.

import unittest
import numpy as np
from MusclePy.solvers.dr.main import main_dynamic_relaxation
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.femodel.pynodes import PyNodes
from MusclePy.femodel.pyelements import PyElements
from MusclePy.solvers.dr.py_elements_dr import PyElementsDR
from MusclePy.solvers.dr.py_truss_dr import PyTrussDR
from MusclePy.solvers.dr.py_nodes_dr import PyNodesDR
from MusclePy.solvers.dr.py_config_dr import PyConfigDR


class TestDR_3SimpleCables(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a 3-cable structure.
        Structure layout:

                  Node 0
                 (2,0,1)
                    | 
                    | cable 0
                    |   
        Node 1 --- Node3 --- Node 2
        (0,0,0)    (2,0,0)   (4,0,0)

        Node 3 is free to move in all directions.
        The structure has a prestress in the first cable.
        """
        # Create nodes
        self.nodes = PyNodes(
            initial_coordinates=np.array([
                [2.0, 0.0, 1.0],  # Node 0: top
                [0.0, 0.0, 0.0],  # Node 1: left
                [4.0, 0.0, 0.0],  # Node 2: right
                [2.0, 0.0, 0.0]   # Node 3: bottom (free)
            ]),
            dof=np.array([
                [False, False, False],  # Node 0: fixed
                [False, False, False],  # Node 1: fixed
                [False, False, False],  # Node 2: fixed
                [True, True, True]      # Node 3: free in all directions
            ])
        )
        
        # Create elements with prestress in cable 0
        cable_area = np.pi * (8 / 2) ** 2  # 8mm diameter cable area in mm²
        self.elements = PyElements(
            nodes=self.nodes,
            type=np.array([1, 1, 1]),  # Three cables
            end_nodes=np.array([[0, 3], [1, 3], [2, 3]]),  # Element connections
            area=np.array([cable_area, cable_area, cable_area]),  # Area in mm²
            youngs=np.array([[70000.0, 70000.0, 70000.0], [70000.0, 70000.0, 70000.0]]),  # 70000 MPa Young's modulus
        )
        
        # Create structure
        self.structure = PyTruss(self.nodes, self.elements)

        # Configure solver
        self.config = PyConfigDR(
            zero_residual_rtol=1e-6,
            zero_residual_atol=1e-6,
            max_time_step=100,
            max_ke_reset=20
        )

    def test_cable_slackening_under_loading(self):
        """Test the 3-cable structure by loading from an unprestressed initial state. cable 0 should go slack under this vertical upward load.
        The test verifies the final tensions and node positions against analytical solutions.
        """
        # first lets ensure cable 0 withstands tension only
        tension_only_elements = PyElements(
            nodes=self.nodes,
            type=self.elements.type,  # Three cables
            end_nodes=self.elements.end_nodes,  # Element connections
            area=self.elements.area,  # Area in mm²
            youngs=np.array([[0.0, 70000.0, 70000.0], [70000.0, 70000.0, 70000.0]])  # 70000 MPa Young's modulus, cable 0 withstands tension only
        )
        tension_only_structure = PyTruss(self.nodes, tension_only_elements)

        # No prestress
        delta_free_length = np.array([0.0,0.0, 0.0])

        # External loads
        loads = np.zeros((4, 3))  # 4 nodes * 3 DOFs
        loads[3, 2] = 888.808  # [N] vertical load at Node 3

        # Solve with dynamic relaxation
        result = main_dynamic_relaxation(
            structure=tension_only_structure,
            loads_increment=loads,
            free_length_variation=delta_free_length,
            config=self.config
        )

        # Verify the solver converged within the maximum number of steps
        self.assertLess(self.config.n_time_step, self.config.max_time_step)
        self.assertLess(self.config.n_ke_reset, self.config.max_ke_reset)

        expected_resisting_force = 888.808  # N
        np.testing.assert_allclose(result.nodes.resisting_forces[3, 2], expected_resisting_force, atol=0.001)

        expected_vertical_reactions = np.array([-444.404, -444.404])  # N
        np.testing.assert_allclose(result.nodes.reactions[[1, 2], 2], expected_vertical_reactions, atol=0.001)

        # Expected tensions from analytical solution
        expected_tensions = np.array([0.0, 7037.17, 7037.17])  # [N] (yielding stress = 140 MPa) * (cable area = 50.26 mm²)
        np.testing.assert_allclose(result.elements.tension, expected_tensions, atol=0.01)

        # Expected final coordinates from analytical solution
        expected_node3_z = 0.126554  # m
        np.testing.assert_allclose(result.nodes.coordinates[3, 2], expected_node3_z, atol=1e-6)




    def test_cable_prestressing(self):
        """Test a 3-cable structure with prestress in cable 0.
        The test verifies the final tensions and node positions against analytical solutions.
        """

        # No external loads
        loads = np.zeros((4, 3))  # 4 nodes * 3 DOFs
        delta_free_length=np.array([-126.775e-3, 0.0, 0.0])  # Prestress first cable

        
        # Solve with dynamic relaxation
        result = main_dynamic_relaxation(
            structure=self.structure,
            loads_increment=loads,
            free_length_variation=delta_free_length,
            config=self.config
        )

        # Verify the solver converged within the maximum number of steps
        self.assertLess(self.config.n_time_step, self.config.max_time_step)
        self.assertLess(self.config.n_ke_reset, self.config.max_ke_reset)

        # Expected tensions from analytical solution
        expected_tensions = np.array([888.808, 7037.17, 7037.17])  # N
        np.testing.assert_allclose(result.elements.tension, expected_tensions, atol=0.01)


        # Expected final coordinates from analytical solution
        expected_node3_z = 0.126554  # m
        np.testing.assert_allclose(result.nodes.coordinates[3, 2], expected_node3_z, atol=1e-6)



if __name__ == '__main__':
    unittest.main()
