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
from MusclePy.solvers.dm.nonlinear_dm import main_nonlinear_displacement_method
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.femodel.pynodes import PyNodes
from MusclePy.femodel.pyelements import PyElements


class TestNonlinearDM_LooseMechanism(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a loose (unprestressed) mechanism.
                Structure layout:

        Node 0----Node 1----Node 2
       (0,0,0)   (1,0,0)    (2,0,0)
             cable1    cable2

        Node 1 is free to move in x and z directions.
        The structure is loaded vertically at Node 1.
        """
        # Create nodes
        self.nodes = PyNodes(
            initial_coordinates=np.array([
                [0.0, 0.0, 0.0],  # Node 0: left support
                [1.0, 0.0, 0.0],  # Node 1: middle point
                [2.0, 0.0, 0.0]   # Node 2: right support
            ]),
            dof=np.array([
                [False, False, False],  # Node 0: fixed
                [True, False, True],    # Node 1: free in x,z
                [False, False, False]   # Node 2: fixed
            ])
        )
        
        # Create elements
        self.elements = PyElements(
            nodes=self.nodes,
            type=np.array([1, 1]),  # Two cables
            end_nodes=np.array([[0, 1], [1, 2]]),  # Element 0: 0->1, Element 1: 1->2
            area=np.array([2500.0, 2500.0]),  # 2500 mm² area
            youngs=np.array([[10000.0, 10000.0], [10000.0, 10000.0]]),  # 10000 MPa Young's modulus
        )
        
        # Create structure
        self.structure = PyTruss(self.nodes, self.elements)

    def test_loads_on_loose_mechanism(self):
        """Test vertical load on the loose mechanism.
        Solution verified against analytical results from Jonas Feron master's thesis p107
        """
        # Apply -100kN vertical load at node 1
        loads = np.zeros(9)  # 3 nodes * 3 DOFs
        loads[5] = -100000.0  # Node 1, Z direction
        
        # Solve with nonlinear solver
        result = main_nonlinear_displacement_method(
            self.structure,
            loads,
            n_steps=100
        )
        
        # Check tensions (analytical solution)
        expected_tensions = np.array([313020.0, 313020.0])  # N
        np.testing.assert_allclose(result.elements.tension, expected_tensions, rtol=2e-2)
        
        # Check final node positions (analytical solution)
        result_coord1z = result.nodes.coordinates[1,2]
        expected_coord1z = -158.74e-3
        np.testing.assert_allclose(result_coord1z, expected_coord1z, rtol=2e-2)



if __name__ == '__main__':
    unittest.main()
