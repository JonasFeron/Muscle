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
from MusclePy.femodel.pynodes import PyNodes
from MusclePy.femodel.pyelements import PyElements
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.solvers.svd.main import main_singular_value_decomposition
from MusclePy.utils.matrix_calculations import compute_equilibrium_matrix


class TestSVD2Cables(unittest.TestCase):
    """Test cases for the SVD computation with a 2-cable structure.
                    Structure layout:

        Node 0----Node 1----Node 2
       (0,0,0)   (1,0,0)    (2,0,0)
             cable1    cable2

        Node 1 is free to move in x, y and z directions.
    """

    def setUp(self):
        """Set up the 2-cable structure for testing."""
        # Create nodes
        coordinates = np.array([
            [0.0, 0.0, 0.0],  # Node 0
            [1.0, 0.0, 0.0],  # Node 1
            [2.0, 0.0, 0.0]   # Node 2
        ])
        
        # Define DOF (True = free, False = fixed)
        dof = np.array([
            False, False, False,  # Node 0: fixed
            True, True, True,     # Node 1: free
            False, False, False   # Node 2: fixed
        ])
        
        nodes = PyNodes(coordinates, dof)
        
        # Create elements
        end_nodes = np.array([
            [0, 1],  # Element 0: connects nodes 0 and 1
            [1, 2]   # Element 1: connects nodes 1 and 2
        ])

        type = [1,1]

        elements = PyElements(nodes=nodes, end_nodes=end_nodes, type = type)
        
        # Create PyTruss
        self.structure = PyTruss(nodes, elements)
        
        # Run SVD analysis
        self.svd_results = main_singular_value_decomposition(self.structure)

    def test_equilibrium_matrix(self):
        """Test the equilibrium matrix computation."""
        # Get equilibrium matrix from the structure
        A_3n = compute_equilibrium_matrix(self.structure.elements.connectivity, self.structure.nodes.coordinates)
        dof = self.structure.nodes.dof.reshape((-1,))
        A = A_3n[dof, :]
        
        # Expected result
        A_expected = np.array([
            [1.0, -1.0],
            [0.0, 0.0],
            [0.0, 0.0]
        ])
        
        # Check result
        self.assertTrue(np.allclose(A, A_expected), 
                        f"Expected:\n{A_expected}\nGot:\n{A}")

    def test_rank(self):
        """Test the rank of the equilibrium matrix."""
        self.assertEqual(self.svd_results.r, 1, "Rank should be 1")
        
    def test_static_indeterminacy(self):
        """Test the degree of static indeterminacy."""
        self.assertEqual(self.svd_results.s, 1, "Static indeterminacy should be 1")
        
    def test_kinematic_indeterminacy(self):
        """Test the degree of kinematic indeterminacy."""
        self.assertEqual(self.svd_results.m, 2, "Kinematic indeterminacy should be 2")
        
    def test_mechanisms(self):
        """Test the mechanisms (inextensional modes)."""
        # Extract the mechanisms from Um and reshape for comparison
        dof = self.structure.nodes.dof.reshape((-1,))
        mechanisms = self.svd_results.Um_T[:,dof]
        expected_mechanisms = np.array([
            [0.0, 1.0, 0.0], # first mechanism: node 1 moves in y direction
            [0.0, 0.0, 1.0] # second mechanism: node 1 moves in z direction
        ])
        
        self.assertTrue(np.allclose(np.abs(mechanisms), np.abs(expected_mechanisms)), 
                        f"Expected mechanisms:\n{expected_mechanisms}\nGot:\n{mechanisms}")
    
    def test_selfstress_modes(self):
        """Test the self-stress modes."""
        # Extract the self-stress modes from Vs
        selfstress_modes = self.svd_results.Vs
        
        # Expected result: [1,1]/sqrt(2)
        expected_selfstress = np.array([1, 1]) / np.sqrt(2)
        
        # Check result - need to use absolute values as signs might differ
        self.assertTrue(np.allclose(np.abs(selfstress_modes), np.abs(expected_selfstress)), 
                        f"Expected self-stress modes:\n{expected_selfstress}\nGot:\n{selfstress_modes}")

if __name__ == '__main__':
    unittest.main()
