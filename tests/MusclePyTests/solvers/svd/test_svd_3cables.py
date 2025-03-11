import unittest
import numpy as np
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.solvers.svd.main import main_singular_value_decomposition
from MusclePy.utils.matrix_calculations import compute_equilibrium_matrix


class TestSVD3Cables(unittest.TestCase):
    """Test cases for the SVD computation with a 3-cable arch structure."""

    def setUp(self):
        """Set up the 3-cable structure for testing.
        see Fig. 12 in  Feron J., Latteur P., Almeida J., 2024, Static Modal Analysis, Arch Comp Meth Eng.
        """
        # Create nodes
        L = 0.16 # m
        coordinates = np.array([
            [0.0, 0.0,  0.0],    # Node 0
            [L  , 0.0, -L/2],    # Node 1
            [2*L, 0.0, -L/2],    # Node 2
            [3*L, 0.0,  0.0]     # Node 3
        ])
        
        # Define DOF (True = free, False = fixed)
        dof = np.array([
            False, False, False,  # Node 0: fixed
            True, False, True,    # Node 1: free in X and Z
            True, False, True,    # Node 2: free in X and Z
            False, False, False   # Node 3: fixed
        ])
        
        nodes = FEM_Nodes(coordinates, dof)
        
        # Create elements
        end_nodes = np.array([
            [0, 1],  # Element 0: connects nodes 0 and 1
            [1, 2],  # Element 1: connects nodes 1 and 2
            [2, 3]   # Element 2: connects nodes 2 and 3
        ])

        elements = FEM_Elements(nodes=nodes, end_nodes=end_nodes)

        # Create FEM_Structure
        self.structure = FEM_Structure(nodes, elements)
        
        # Run SVD analysis
        self.svd_results = main_singular_value_decomposition(self.structure)

    def test_rank(self):
        # Check rank
        self.assertEqual(self.svd_results.r, 3,
                         f"Expected rank: 3, Got: {self.svd_results.r}")

    def test_static_indeterminacy(self):
        # Check static indeterminacy
        self.assertEqual(self.svd_results.s, 0, 
                         f"Expected static indeterminacy: 0, Got: {self.svd_results.s}")

    def test_kinematic_indeterminacy(self):
        # Check kinematic indeterminacy
        self.assertEqual(self.svd_results.m, 1,
                         f"Expected kinematic indeterminacy: 1, Got: {self.svd_results.m}")

    def test_mechanisms(self):
        """Test the mechanisms (inextensional modes)."""
        # Extract the mechanisms from Um and reshape for comparison
        dof = self.structure.nodes.dof.reshape((-1,))
        mechanisms = self.svd_results.Um_T[:, dof]
        expected_mechanisms = np.array([
            [-0.5, -1, -0.5, 1]/np.sqrt(2.5)  # first mechanism
        ])

        self.assertTrue(np.allclose(mechanisms, expected_mechanisms),
                        f"Expected mechanisms:\n{expected_mechanisms}\nGot:\n{mechanisms}")

if __name__ == '__main__':
    unittest.main()
