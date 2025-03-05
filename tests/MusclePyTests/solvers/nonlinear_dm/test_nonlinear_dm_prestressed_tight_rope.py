import unittest
import numpy as np
from MusclePy.solvers.nonlinear_dm.nonlinear_dm import NonlinearDisplacementMethod
from MusclePy.solvers.linear_dm.linear_dm import LinearDisplacementMethod
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements


class TestNonlinearDM_PrestressedTightRope(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a prestressed tight rope structure.
        Node 0----Node 1----Node 2
       (0,0,0)   (1,0,0)    (2,0,0)
             cable1    cable2

        Node 1 is free to move in x and z directions.
        The structure will be prestressed and then loaded vertically at Node 1.
        """
        # Create nodes
        self.nodes = FEM_Nodes(
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
        self.elements = FEM_Elements(
            nodes=self.nodes,
            type=np.array([1, 1]),  # Two cables
            end_nodes=np.array([[0, 1], [1, 2]]),  # Element 0: 0->1, Element 1: 1->2
            areas=np.array([[50.0, 50.0], [50.0, 50.0]]),  # 50 mm² area
            youngs=np.array([[100000.0, 100000.0], [100000.0, 100000.0]]),  # 100 GPa Young's modulus
            delta_free_length=np.array([0.0, 0.0]),  # No initial prestress
            tension=np.array([0.0, 0.0])  # No initial tension
        )
        
        # Create structure
        self.structure = FEM_Structure(self.nodes, self.elements)

    def test_3stage_loading(self):
        """Test tight rope structure through 3 loading stages:
        1. Initial prestress through free length changes
        2. First load increment
        3. Second load increment
        
        Solution verified against analytical results available in provided excel file
        """
        # Stage 1: Apply prestress through free length changes
        delta_free_length_increment = np.array([-3.984e-3, -3.984e-3]) 
        prestressed_structure = LinearDisplacementMethod.apply_loads_and_prestress_increments(
            self.structure,
            np.zeros(9),  # No external loads
            delta_free_length_increment
        )
        # Check prestress forces
        expected_prestress = np.array([20000.0, 20000.0])  # N
        np.testing.assert_allclose(prestressed_structure.elements.tension, expected_prestress, rtol=2e-2)
        

        
        # Stage 2: Apply first load increment
        loads1 = np.zeros(9)
        loads1[5] = -5109.0  # Node 1, Z direction
        
        stage1 = NonlinearDisplacementMethod.incremental_newton_raphson_procedure(
            prestressed_structure,
            loads1,
            n_steps=100
        )
        
        # Check stage 1 results
        expected_displacement1 = -75.0e-3  # m
        expected_tension1 = 34043.0  # N
        
        d1 = stage1.nodes.coordinates - prestressed_structure.nodes.coordinates
        np.testing.assert_allclose(d1.reshape(-1,3)[1,2], expected_displacement1, rtol=2e-2)
        np.testing.assert_allclose(stage1.elements.tension, np.array([expected_tension1, expected_tension1]), rtol=2e-2)
        
        # Stage 3: Apply second load increment
        loads2 = np.zeros(9)
        loads2[5] = -9988.0  # Node 1, Z direction
        
        stage2 = NonlinearDisplacementMethod.incremental_newton_raphson_procedure(
            stage1,
            loads2 - loads1,  # Additional load increment
            n_steps=100
        )
        
        # Check stage 2 results
        expected_displacement2 = -105.0e-3  # m
        expected_tension2 = 47487.0  # N
        
        d2 = stage2.nodes.coordinates - prestressed_structure.nodes.coordinates
        np.testing.assert_allclose(d2.reshape(-1,3)[1,2], expected_displacement2, rtol=2e-2)
        np.testing.assert_allclose(stage2.elements.tension, np.array([expected_tension2, expected_tension2]), rtol=2e-2)


if __name__ == '__main__':
    unittest.main()
