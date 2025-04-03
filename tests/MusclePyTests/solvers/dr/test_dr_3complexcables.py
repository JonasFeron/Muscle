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
from musclepy.solvers.dr.main import main_dynamic_relaxation
from musclepy.femodel.pytruss import PyTruss
from musclepy.femodel.pynodes import PyNodes
from musclepy.femodel.pyelements import PyElements
from musclepy.solvers.dr.py_elements_dr import PyElementsDR
from musclepy.solvers.dr.py_truss_dr import PyTrussDR
from musclepy.solvers.dr.py_nodes_dr import PyNodesDR
from musclepy.solvers.dr.py_config_dr import PyConfigDR


class TestDR_3ComplexCables(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a 3-cable structure with reorientation of the shortening axis.
        Structure layout:

        Node 0
        (0,0,1)
               \
                \  cable 0 
                 \ 
                  \ 
        Node 1 --- Node3 --- Node 2
        (0,0,0)    (2,0,0)   (4,0,0)
              cable1    cable2

        Node 3 is free to move in all directions.
        The structure has a prestress in cable 0.
        """
        # Create nodes
        self.nodes = PyNodes(
            initial_coordinates=np.array([
                [0.0, 0.0, 1.0],  # Node 0: top
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
        
        # Create elements
        cable_area =  np.pi * (8/2)**2  # 8mm diameter cable area in mm²
        self.elements = PyElements(
            nodes=self.nodes,
            type=np.array([1, 1, 1]),  # Three cables
            end_nodes=np.array([[0, 3], [1, 3], [2, 3]]),  # Element connections
            area=np.array([cable_area, cable_area, cable_area]),  # Area in mm²
            youngs=np.array([[0.0, 70000.0, 70000.0], [70000.0, 70000.0, 70000.0]]),  # 70000 MPa Young's modulus. Cable 0 can only be in tension.
        )
        
        # Create structure
        self.structure = PyTruss(self.nodes, self.elements)

        # Configure solver with higher precision
        self.config = PyConfigDR(
            zero_residual_atol=1e-6,
            max_time_step=150,
            max_ke_reset=30
        )

    def test_nonlinear_prestress(self):
        """Test the complex 3-cable structure by prestressing cable 0 with axis reorientation of the cable being prestressed.
        The test verifies the final tensions and node positions against analytical solutions.
        """
        # No external loads
        loads = np.zeros((4, 3))  # 4 nodes * 3 DOFs
        
        # Apply prestress to the first cable
        delta_free_length = np.array([-52.110e-3, 0.0, 0.0])  # m
        
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
        expected_tensions = np.array([1823.48, 5365.62, 7037.17])  # N
        np.testing.assert_allclose(result.elements.tension, expected_tensions, atol=0.2)

        # Expected final coordinates from analytical solution
        expected_node3_coords = np.array([2.0-0.000476, 0.0, 0.118795])  # m
        np.testing.assert_allclose(result.nodes.coordinates[3], expected_node3_coords, atol=1e-6)



    def test_cable_slackening(self):
        """Test a 3-cable structure by prestressing cable 1 which means cable 0 is slack.
        The test verifies that the slack cable has zero tension and the structure
        finds equilibrium with only cable 1 and 2.
        """
        # No external loads
        loads = np.zeros((4, 3))  # 4 nodes * 3 DOFs
        
        # Apply prestress to cable 1
        delta_free_length = np.array([0.0, -7.984e-3, 0.0])  # m
        
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
        expected_tensions = np.array([0.0, 7037.17, 7037.17])  # N
        np.testing.assert_allclose(result.elements.tension, expected_tensions, atol=0.04)

        
        # Expected final coordinates from analytical solution
        expected_node3_coords = np.array([2.0-0.004000, 0.0, 0.0])  # m
        np.testing.assert_allclose(result.nodes.coordinates[3], expected_node3_coords, atol=1e-6)




if __name__ == '__main__':
    unittest.main()
