import unittest
import numpy as np
from MusclePy.femodel.pynodes import PyNodes
from MusclePy.femodel.pyelements import PyElements
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.solvers.dr.main import main_dynamic_relaxation
from MusclePy.solvers.dr.py_config_dr import PyConfigDR
from MusclePy.solvers.dynamic.py_results_dynamic import PyResultsDynamic
from MusclePy.solvers.dynamic.main import main_dynamic_modal_analysis, _compute_mass_matrix, _compute_tangent_stiffness_matrix


class TestDynamicSimplex(unittest.TestCase):
    """Test cases for the dynamic modal analysis with an experimental simplex structure.
    """

    def setUp(self):
        """Set up the experimental simplex structure for testing.

        Note that set up is sligtly different than for the static case.
        The loading plate is now attached to the top nodes resulting in different mass for the top nodes

        """


        # Create nodes
        coordinates = np.array([      # in [m]
            [0.00, -2043.8, 0.00],     # Node 0
            [0.00, 0.00, 0.00],        # Node 1
            [1770.00, -1021.9, 0.00],  # Node 2
            [590.00, -2201.9, 1950.00], # Node 3
            [-431.9, -431.9, 1950.00],  # Node 4
            [1611.9, -431.9, 1950.00]   # Node 5
        ])/1000
        
        # Define DOF (True = free, False = fixed)
        dof = np.array([
            False, True, False,    # Node 0
            False, False, False,   # Node 1
            True, True, False,     # Node 2
            True, True, True,      # Node 3
            True, True, True,      # Node 4
            True, True, True       # Node 5
        ])
        
        nodes = PyNodes(coordinates, dof)
        
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
        elementsA = np.ones(12)
        elementsA[0:3] = 364.4 # struts 
        elementsA[3:12] = 50.3 # cables

        elements = PyElements(nodes=nodes, end_nodes=end_nodes, type=elements_type, youngs=elementsE, area=elementsA)
        
        # Create PyTruss
        self.structure = PyTruss(nodes, elements)

        # Set free length variation for initial self-stress level = 1.5kN
        free_length_variation = np.zeros(12)
        free_length_variation[0:3] = +0.717/1000  # [m] struts
       
        # self-weight (including element weight)
        self_weight = np.array([
            [0.0, 0.0, -45.7],     # Node 0
            [0.0, 0.0, -45.7],        # Node 1
            [0.0, 0.0, -45.7],  # Node 2
            [0.0, 0.0, -50.3],  # Node 3
            [0.0, 0.0, -50.3],  # Node 4
            [0.0, 0.0, -50.3]   # Node 5
        ])

        # Point mass (nodes only)(active in the 3 directions)
        self.point_mass = np.zeros((6, 3))
        self.point_mass[0:3, [0,1,2]] = 2.642  # kg, bottom nodes mass
        self.point_mass[3:6, [0,1,2]] = 3.06  # kg, top nodes mass including loading plate

        # Element mass (elements only)
        self.element_mass = np.zeros(12)
        self.element_mass[0:3] = 2.63  # kg, struts, including accelerometer
        self.element_mass[3:12] = 0.502  # kg, cables                


        # Configure solver
        self.config = PyConfigDR(
            zero_residual_rtol=1e-4, 
            zero_residual_atol=1e-6,
            max_time_step=1000,
            max_ke_reset=100,
        )

        # Run form-finding analysis
        self.form_found_structure = main_dynamic_relaxation(
            structure=self.structure,
            loads_increment=self_weight,
            free_length_variation=free_length_variation,
            config=self.config
        )


        #expected results:
        # Expected total masses (nodes + elements)
        self.expected_masses = np.zeros((6, 3))
        self.expected_masses[0:3, [0,1,2]] = 4.70 # kg, total mass applied on bottom nodes
        self.expected_masses[3:6, [0,1,2]] = 5.13  # kg, total mass applied on top nodes


        # Check First dynamic mode = mechanism
        expected_scaled_mechanism = np.array([
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0],
            [ 3.3,    0, -1.0],
            [-1.7, -2.9, -1.0],
            [-1.7,  2.9, -1.0],
        ]).reshape((-1,))
        norm = np.linalg.norm(expected_scaled_mechanism)
        self.expected_mechanism = expected_scaled_mechanism/norm

    def test_consistent_mass_matrix(self):
        """Test the dynamic modal analysis with consistent mass matrix formulation.
        
        This test verifies:
        1. The form-finding results in the expected axial forces in the struts (-1.5kN)
        2. The mass matrix has the correct shape and values
        3. The first natural mode corresponds to the expected mechanism
        4. The first natural frequency is approximately 2.346 Hz
        
        The consistent mass matrix formulation is more accurate than the lumped mass matrix
        as it accounts for the distribution of mass along elements.
        """
        # assert that the axial force in the three struts is almost -1.5kN
        self.assertAlmostEqual(self.form_found_structure.elements.tension[0:3].mean(), -1500, delta=1)

        results = main_dynamic_modal_analysis(
            structure=self.form_found_structure,
            point_masses=self.point_mass,
            element_masses=self.element_mass,
            element_masses_option=2,
            n_modes=0
        )


        # Check mass matrix
        self.assertEqual(results.mass_matrix.shape, (18, 18),
                         f"Expected mass matrix shape: (18, 18), Got: {results.mass_matrix.shape}")

        self.assertEqual(results.masses.shape, (18,),
                         f"Expected masses shape: (18,), Got: {results.masses.shape}")

        self.assertTrue(np.allclose(results.masses.reshape(-1,3), self.expected_masses, atol=0.01),
                        f"Expected total masses:\n{self.expected_masses}\nGot:\n{results.masses.reshape(-1,3)}")

        # check n_modes
        self.assertEqual(results.mode_count, 12,
                         f"Expected number of natural modes: 12, Got: {results.mode_count}")

        # check mode_shapes
        self.assertEqual(results.mode_shapes.shape, (12, 18),
                         f"Expected mode shapes shape: (12, 18), Got: {results.mode_shapes.shape}")

        # Get the first natural mode and normalize it
        first_natural_mode = results.mode_shapes[0]
        first_mode_norm = np.linalg.norm(first_natural_mode)
        normalized_first_mode = first_natural_mode / first_mode_norm
        
        # Check if the first 9 elements (fixed DOFs) are close to zero
        self.assertTrue(np.allclose(normalized_first_mode[:9], 0, atol=0.01),
                        f"Expected first 9 elements to be close to zero, but got:\n{normalized_first_mode[:9]}")
        
        # Check if the pattern of the non-zero elements matches the expected mechanism
        actual_dynamic_mode = np.abs(normalized_first_mode[9:])
        expected_abs_mechanism = np.abs(self.expected_mechanism[9:])
        
        self.assertTrue(np.allclose(actual_dynamic_mode, expected_abs_mechanism, atol=0.015),
                        f"Expected mechanism pattern:\n{expected_abs_mechanism}\nGot:\n{actual_dynamic_mode}")


        # check natural frequency
        self.assertAlmostEqual(results.frequencies[0], 2.346, delta=0.001)

    def test_lumped_mass_matrix(self):
        """Test the dynamic modal analysis with lumped mass matrix formulation.
        
        This test verifies:
        1. The form-finding results in the expected axial forces in the struts (-1.5kN)
        2. The mass matrix has the correct shape and values
        3. The first natural mode corresponds to the expected mechanism
        4. The eigenvalue equation (K·φ = ω²·M·φ) is satisfied for the first mode
        5. The first natural frequency is approximately 2.166 Hz
        
        The lumped mass matrix formulation simplifies the mass distribution by
        concentrating element masses at the nodes, resulting in a diagonal mass matrix.
        """
        # assert that the axial force in the three struts is almost -1.5kN
        self.assertAlmostEqual(self.form_found_structure.elements.tension[0:3].mean(), -1500, delta=1)

        results = main_dynamic_modal_analysis(
            structure=self.form_found_structure,
            point_masses=self.point_mass,
            element_masses=self.element_mass,
            element_masses_option=1, #lumped
            n_modes=0
        )


        # Check mass matrix
        self.assertEqual(results.mass_matrix.shape, (18, 18),
                         f"Expected mass matrix shape: (18, 18), Got: {results.mass_matrix.shape}")

        self.assertEqual(results.masses.shape, (18,),
                         f"Expected masses shape: (18,), Got: {results.masses.shape}")

        self.assertTrue(np.allclose(np.diag(results.mass_matrix).reshape(-1,3), self.expected_masses, atol=0.01),
                        f"Expected total masses:\n{self.expected_masses}\nGot:\n{np.diag(results.mass_matrix)}")

        # check n_modes
        self.assertEqual(results.mode_count, 12,
                         f"Expected number of natural modes: 12, Got: {results.mode_count}")

        # check mode_shapes
        self.assertEqual(results.mode_shapes.shape, (12, 18),
                         f"Expected mode shapes shape: (12, 18), Got: {results.mode_shapes.shape}")

        # Get the first natural mode and normalize it
        mode0 = results.mode_shapes[0]
        mode0_norm = np.linalg.norm(mode0)
        mode0_normed = mode0 / mode0_norm

        # Check if the first 9 elements (fixed DOFs) are close to zero
        self.assertTrue(np.allclose(mode0_normed[:9], 0, atol=0.01),
                        f"Expected first 9 elements to be close to zero, but got:\n{mode0_normed[:9]}")

        # Check if the pattern of the non-zero elements matches the expected mechanism
        actual_dynamic_mode = np.abs(mode0_normed[9:])
        expected_abs_mechanism = np.abs(self.expected_mechanism[9:])

        self.assertTrue(np.allclose(actual_dynamic_mode, expected_abs_mechanism, atol=0.015),
                        f"Expected mechanism pattern:\n{expected_abs_mechanism}\nGot:\n{actual_dynamic_mode}")

        # Check eigen value solver
        eigenvalue0 = results.angular_frequencies[0]**2
        K_3n = _compute_tangent_stiffness_matrix(self.form_found_structure)
        M_3n = _compute_mass_matrix(self.form_found_structure, self.point_mass, self.element_mass, 1)

        vector_lhs = K_3n @ mode0
        vector_rhs = eigenvalue0 * M_3n @ mode0
        dof = self.form_found_structure.nodes.dof.reshape((-1,))

        self.assertTrue(np.allclose(vector_lhs[dof], vector_rhs[dof], atol=0.001),
                        f"Expected eigenvector :\n{vector_lhs}\nGot:\n{vector_rhs}")


        # check natural frequency
        self.assertAlmostEqual(results.frequencies[0], 2.166, delta=0.001)


    def test_partial_eigenvalue_solver(self):
        """Test the dynamic modal analysis with partial eigenvalue computation.
        
        This test verifies:
        1. The form-finding results in the expected axial forces in the struts (-1.5kN)
        2. The solver correctly computes only the requested number of modes (3)
        3. The first natural mode corresponds to the expected mechanism
        4. The first natural frequency is approximately 2.166 Hz
        
        This test ensures that the eigenvalue solver works correctly when only
        a subset of the modes is requested, which is important for large structures
        where computing all modes would be computationally expensive.
        """
        # assert that the axial force in the three struts is almost -1.5kN
        self.assertAlmostEqual(self.form_found_structure.elements.tension[0:3].mean(), -1500, delta=1)

        results = main_dynamic_modal_analysis(
            structure=self.form_found_structure,
            point_masses=self.point_mass,
            element_masses=self.element_mass,
            element_masses_option=1, #lumped
            n_modes=3 # compute only 3 modes
        )


        # check n_modes
        self.assertEqual(results.mode_count, 3,
                         f"Expected number of natural modes: 3, Got: {results.mode_count}")

        # check mode_shapes
        self.assertEqual(results.mode_shapes.shape, (3, 18),
                         f"Expected mode shapes shape: (3, 18), Got: {results.mode_shapes.shape}")

        # Get the first natural mode and normalize it
        mode0 = results.mode_shapes[0]
        mode0_norm = np.linalg.norm(mode0)
        mode0_normed = mode0 / mode0_norm

        # Check first mode follow the mechanism direction
        actual_dynamic_mode = np.abs(mode0_normed[9:])
        expected_abs_mechanism = np.abs(self.expected_mechanism[9:])

        self.assertTrue(np.allclose(actual_dynamic_mode, expected_abs_mechanism, atol=0.015),
                        f"Expected mechanism pattern:\n{expected_abs_mechanism}\nGot:\n{actual_dynamic_mode}")

        # check natural frequency
        self.assertAlmostEqual(results.frequencies[0], 2.166, delta=0.001)

if __name__ == '__main__':
    unittest.main()
