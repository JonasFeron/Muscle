import unittest
import numpy as np
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.solvers.svd.structure_svd import Structure_SVD
from MusclePy.solvers.svd.svd import SingularValueDecomposition
from MusclePy.solvers.svd.self_stress_modes import SelfStressModes
from MusclePy.solvers.dm.model.dm_elements import DM_Elements
from MusclePy.solvers.dm.model.dm_structure import DM_Structure




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

        # Set element types (1 for cables, -1 for struts)
        elements_type = np.ones(12)
        elements_type[[0, 1, 2]] = -1  # struts

        # Set Young moduli [in compression, in tension] MPa
        # Struts can only be in compression and cables only in tension
        elementsE = np.array([[70390, 0],
                              [70390, 0],
                              [70390, 0],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 72190],
                              [0, 72190],
                              [0, 72190]])  

        # Set cross-sectional areas [mm²]
        elementsA = np.ones((12,2))
        elementsA[0:3,:] = 364.4 # struts 
        elementsA[3:12,:] = 50.3 # cables
        
        elements = FEM_Elements(nodes=nodes, end_nodes=end_nodes, type=elements_type, youngs=elementsE, areas=elementsA)
        
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

    def test_localize_self_stress_modes(self):
        """Test the localization of self-stress modes.
        See Fig 3. in Feron, Rhode-Barbarigos, Latteur, 2023, Experimental testing of a tensegrity simplex, JSE
        """

        # Get the self-stress modes from SVD
        Vs_T = self.svd_results.Vs_T

        # Check static indeterminacy
        self.assertEqual(Vs_T.shape[0], 1, 
                         f"Expected static indeterminacy: 1, Got: {Vs_T.shape[0]}")
               
        # Apply normalization
        S_T = SelfStressModes._normalize(Vs_T)

        expected_mode = np.array([
            [-1.0, -1.0, -1.0, 0.393, 0.393, 0.393, 0.393, 0.393, 0.393, 0.681, 0.681, 0.681]
        ])

        self.assertTrue(np.allclose(np.abs(S_T), np.abs(expected_mode), atol=0.001),
                        f"Expected localized modes:\n{expected_mode}\nGot:\n{S_T}")


    def test_global_material_stiffness(self):
        """Test the global material stiffness from two methods"""

        # 1) Get the global material stiffness - computed based on the equilibrium matrix - within Structure_SVD
        global_material_stiffness = self.structure.global_material_stiffness_matrix

        # 2) Get the global material stiffness - computed based on the local stiffness matrix of each element - within Structure_Linear_DM
        # 2a) compute the local stiffness matrix of each element
        dm_elements = DM_Elements(
            self.structure.nodes,
            self.structure.elements.type,
            self.structure.elements.end_nodes,
            self.structure.elements.areas,
            self.structure.elements.youngs
            )
        # 2b) compute the global stiffness matrix
        dm_structure = DM_Structure(self.structure.nodes, dm_elements) 
        global_material_stiffness_linear_dm = dm_structure.global_material_stiffness_matrix

        self.assertTrue(np.allclose(global_material_stiffness, global_material_stiffness_linear_dm),
                        f"Expected global material stiffness:\n{global_material_stiffness_linear_dm}\nGot:\n{global_material_stiffness}")

if __name__ == '__main__':
    unittest.main()
