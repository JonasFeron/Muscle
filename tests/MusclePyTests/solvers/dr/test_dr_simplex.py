import unittest
import numpy as np
from MusclePy.solvers.dr.main import main_dynamic_relaxation
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.solvers.dr.dr_elements import DR_Elements
from MusclePy.solvers.dr.dr_structure import DR_Structure
from MusclePy.solvers.dr.dr_nodes import DR_Nodes
from MusclePy.solvers.dr.dr_config import DRconfig


class TestDR_Simplex(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a simplex tensegrity structure.
        This structure matches the experimental simplex from Landolf Rhode Barbarigos,
        with shortening of one horizontal cable.
        """
        # Create nodes
        self.nodes = FEM_Nodes(
            initial_coordinates=np.array([
                [   0.00, -2043.82, 0.00],  # Node 0
                [   0.00,     0.00, 0.00],  # Node 1
                [1770.00, -1021.91, 0.00],  # Node 2
                [ 590.00, -2201.91, 1950.00],  # Node 3
                [-431.91,  -431.91, 1950.00],  # Node 4
                [1611.91,  -431.91, 1950.00]   # Node 5
            ])*1e-3,  # Convert to meters
            dof=np.array([
                [False, True, False],    # Node 0: y free
                [False, False, False],   # Node 1: fixed
                [True, True, False],     # Node 2: x,y free
                [True, True, True],      # Node 3: all free
                [True, True, True],      # Node 4: all free
                [True, True, True]       # Node 5: all free
            ])
        )
        
        # Create elements (3 struts and 9 cables)
        # Struts can only be in compression, cables only in tension

        areas = np.ones((12, 2))
        areas[0:3, :] = 364.4  # Struts area in mm²
        areas[3:12, :] = 50.3  # Cables area in mm²

        self.elements = FEM_Elements(
            nodes=self.nodes,
            type=np.array([-1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1]),  # -1: strut, 1: cable
            end_nodes=np.array([
                [2, 4],  # Strut 0
                [1, 3],  # Strut 1
                [0, 5],  # Strut 2
                [1, 2],  # Cable 0
                [0, 1],  # Cable 1
                [0, 2],  # Cable 2
                [4, 5],  # Cable 3
                [3, 4],  # Cable 4
                [3, 5],  # Cable 5
                [2, 5],  # Cable 6
                [1, 4],  # Cable 7
                [0, 3]   # Cable 8
            ]),
            areas=areas,
            youngs=np.array([
                [70390, 0],  # Strut 0: E_compression = 70390 MPa, E_tension = 0
                [70390, 0],  # Strut 1
                [70390, 0],  # Strut 2
                [0, 71750],  # Cable 0: E_compression = 0, E_tension = 71750 MPa
                [0, 71750],  # Cable 1
                [0, 71750],  # Cable 2
                [0, 71750],  # Cable 3
                [0, 71750],  # Cable 4
                [0, 71750],  # Cable 5
                [0, 71750],  # Cable 6
                [0, 71750],  # Cable 7
                [0, 71750]   # Cable 8
            ])
        )
        
        # Create structure
        self.structure = FEM_Structure(self.nodes, self.elements)

        # Configure solver
        self.config = DRconfig(
            zero_residual_rtol=1e-4, 
            zero_residual_atol=1e-6,
            max_time_step=1000,
            max_ke_reset=100,
        )

    def test_simplex_with_cable_shortening(self):
        """Test a simplex tensegrity structure with shortening of one horizontal cable.
        The test verifies the final tensions and node positions against results from
        Landolf Rhode Barbarigos' MATLAB implementation.
        """
        # Apply loads (gravity)
        loads = np.zeros((6, 3))
        loads[0:3, 2] = 45.7  # N, vertical load on bottom nodes
        loads[3:6, 2] = 41.6  # N, vertical load on top nodes
        
        # Apply lengthenings
        delta_free_length = np.zeros(12)  # m
        delta_free_length[0:3] = 0.835e-3  # Struts
        delta_free_length[8] = -35e-3  # Shortening of cable 5 (index 8)
        
        # Solve with dynamic relaxation
        result = main_dynamic_relaxation(
            structure=self.structure,
            loads_increment=loads,
            free_length_variation=delta_free_length,
            config=self.config
        )
        
        # Expected tensions from MATLAB implementation
        expected_tensions = np.array([
            -9848.26151894298,  # Strut 0
            -9882.41664832343,  # Strut 1
            -9874.50280077890,  # Strut 2
            3953.87930064950,   # Cable 0
            3835.52819661200,   # Cable 1
            3808.51599478652,   # Cable 2
            3859.21359327111,   # Cable 3
            3858.16975358279,   # Cable 4
            3947.80984861979,   # Cable 5
            6653.65253640084,   # Cable 6
            6677.35302197632,   # Cable 7
            6744.48294062936    # Cable 8
        ])  # N

        # Verify the solver converged within the maximum number of steps
        self.assertLess(self.config.n_time_step, self.config.max_time_step)
        self.assertLess(self.config.n_ke_reset, self.config.max_ke_reset)

        # Expected final coordinates from MATLAB implementation
        expected_coordinates = np.array([
            [   0.00, -2045.97206933403, 0.00],
            [   0.00,     0.00, 0.00],
            [1771.89364968302, -1023.06835531595, 0.00],
            [ 616.024764975095, -2197.43254689303, 1946.45254155930],
            [-427.528116330227, -437.602999235727, 1953.63046329029],
            [1618.37958793442, -454.066751469362, 1960.50103999593]
        ])*1e-3  # m
        
        # Check final tensions
        np.testing.assert_allclose(result.elements.tension, expected_tensions, rtol=1e-2)
        
        # Check final node positions
        np.testing.assert_allclose(result.nodes.coordinates.flatten(), expected_coordinates.flatten(), rtol=1e-2, atol=1e-3)


if __name__ == '__main__':
    unittest.main()
