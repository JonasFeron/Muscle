import unittest
import numpy as np
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.solvers.svd.structure_svd import Structure_SVD
from MusclePy.solvers.svd.svd import SingularValueDecomposition


class TestSVDSimplex(unittest.TestCase):
    """Test cases for the SVD computation with an experimental simplex structure.
    see Fig. 1 in Feron, Rhode-Barbarigos, Latteur, 2023, Experimental testing of a tensegrity simplex, JSE
    """

    def setUp(self):
        """Set up the experimental simplex structure for testing."""
        # Create nodes
        coordinates = np.array([
            [0.00, -2043.8, 0.00],     # Node 0
            [0.00, 0.00, 0.00],        # Node 1
            [1770.00, -1021.9, 0.00],  # Node 2
            [590.00, -2201.9, 1950.00], # Node 3
            [-431.9, -431.9, 1950.00],  # Node 4
            [1611.9, -431.9, 1950.00]   # Node 5
        ])
        
        # Define DOF (True = free, False = fixed)
        dof = np.array([
            False, True, False,    # Node 0
            False, False, False,   # Node 1
            True, True, False,     # Node 2
            True, True, True,      # Node 3
            True, True, True,      # Node 4
            True, True, True       # Node 5
        ])
        
        nodes = FEM_Nodes(coordinates, dof)
        
        # Create elements
        end_nodes = np.array([
            [2, 4],   # Element 0
            [1, 3],   # Element 1
            [0, 5],   # Element 2
            [1, 2],   # Element 3
            [0, 1],   # Element 4
            [0, 2],   # Element 5
            [4, 5],   # Element 6
            [3, 4],   # Element 7
            [3, 5],   # Element 8
            [2, 5],   # Element 9
            [1, 4],   # Element 10
            [0, 3]    # Element 11
        ])
        
        elements = FEM_Elements(nodes=nodes, end_nodes=end_nodes)
        
        # Create Structure_SVD
        self.structure = Structure_SVD(nodes, elements)
        
        # Run SVD analysis
        self.svd_results = SingularValueDecomposition.core(self.structure,zero_tol=1e-3)

    def test_rank(self):
        # Check rank
        self.assertEqual(self.svd_results.r, 11,
                         f"Expected rank: 11, Got: {self.svd_results.r}")

    def test_static_indeterminacy(self):
        # Check static indeterminacy
        self.assertEqual(self.svd_results.s, 1,
                         f"Expected static indeterminacy: 1, Got: {self.svd_results.s}")

    def test_kinematic_indeterminacy(self):
        # Check kinematic indeterminacy
        self.assertEqual(self.svd_results.m, 1,
                         f"Expected kinematic indeterminacy: 1, Got: {self.svd_results.m}")

    def test_mechanisms(self):
        """Test the mechanisms (inextensional modes).
        See Fig 4. in Feron, Rhode-Barbarigos, Latteur, 2023, Experimental testing of a tensegrity simplex, JSE
        """
        dof = self.structure.nodes.dof.reshape((-1,))
        mechanisms = self.svd_results.Um_T[:, dof].reshape((-1,))

        expected_scaled_mechanism = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [ 3.3,    0, -1.0],
            [-1.7, -2.9, -1.0],
            [-1.7,  2.9, -1.0],
        ]).reshape((-1,))
        norm = np.linalg.norm(expected_scaled_mechanism)

        expected_mechanism = expected_scaled_mechanism[dof]/norm

        rounding_error = 0.1/norm

        self.assertTrue(np.allclose(np.abs(mechanisms), np.abs(expected_mechanism), atol=rounding_error),
                        f"Expected mechanisms:\n{expected_mechanism}\nGot:\n{mechanisms}")

    # def test_selfstress_modes(self):
    #     """Test the self-stress modes.
    #     See Fig 3. in Feron, Rhode-Barbarigos, Latteur, 2023, Experimental testing of a tensegrity simplex, JSE
    #
    #     """
    #     # Extract the self-stress modes from Vs
    #     selfstress_modes = self.svd_results.Vs
    #
    #     # Expected result: [1,1]/sqrt(2)
    #     expected_selfstress = np.array([1, 1]) / np.sqrt(2)
    #
    #     # Check result - need to use absolute values as signs might differ
    #     self.assertTrue(np.allclose(np.abs(selfstress_modes), np.abs(expected_selfstress)),
    #                     f"Expected self-stress modes:\n{expected_selfstress}\nGot:\n{selfstress_modes}")

if __name__ == '__main__':
    unittest.main()
