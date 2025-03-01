import unittest
import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../src/MusclePy'))
sys.path.append(base_dir)
import numpy as np
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements


class TestFEMElements(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a simple 2-bar structure.
           Node 1 (1,0,1)
           /\
          /  \
         /    \
        Node 0  Node 2
        (0,0,0) (2,0,0)
        """
        # Create nodes instance first
        self.nodes = FEM_Nodes(
            initial_coordinates=np.array([
                [0.0, 0.0, 0.0],  # Node 0: origin
                [1.0, 0.0, 1.0],  # Node 1: top
                [2.0, 0.0, 0.0]   # Node 2: right
            ]),
            dof=np.array([
                [False, False, False],  # Node 0: fixed
                [True, False, True],    # Node 1: free in x,z
                [False, False, False]   # Node 2: fixed
            ])
        )
        
        # Create elements instance
        self.elements = FEM_Elements(
            nodes=self.nodes,
            type=np.array([-1, -1]),  # Two struts
            end_nodes=np.array([[0, 1], [1, 2]]),  # Element 0: 0->1, Element 1: 1->2
            areas=np.array([[2500.0, 1000.0], [2500.0, 1000.0]]),  # different areas in compression/tension
            youngs=np.array([[10000.0, 10000.0], [10000.0, 10000.0]]),  # Same Young's modulus
            delta_free_length=np.array([0.0, 0.0]),  # No initial prestress
            tension=np.array([0.0, 0.0])  # No initial tension
        )

    def test_initialization(self):
        """Test proper initialization of FEM_Elements."""
        self.assertEqual(self.elements.count, 2)
        self.assertEqual(len(self.elements.type), 2)
        self.assertEqual(self.elements.end_nodes.shape, (2, 2))
        np.testing.assert_array_equal(self.elements.type, [-1, -1])
        
    def test_initial_free_length(self):
        """Test computation of initial free length."""
        expected_lengths = np.array([
            np.sqrt(1.0**2 + 1.0**2),  # Element 0: sqrt(2)
            np.sqrt(1.0**2 + 1.0**2)   # Element 1: sqrt(2)
        ])
        np.testing.assert_array_almost_equal(self.elements.initial_free_length, expected_lengths)
        
    def test_connectivity_matrix(self):
        """Test computation of connectivity matrix."""
        expected_connectivity = np.array([
            [-1, 1, 0],   # Element 0: node0 -> node1
            [0, -1, 1]    # Element 1: node1 -> node2
        ])
        np.testing.assert_array_equal(self.elements.connectivity, expected_connectivity)
        
    def test_current_properties(self):
        """Test computation of current properties based on tension state."""
        # Test with compression (negative tension)
        compressed_elements = self.elements.copy_and_update(
            nodes=self.nodes,
            delta_free_length=self.elements.delta_free_length,
            tension=np.array([-1000.0, -1000.0])
        )
        np.testing.assert_array_equal(compressed_elements.area, [2500.0, 2500.0])
        np.testing.assert_array_equal(compressed_elements.young, [10000.0, 10000.0])
        
        # Test with tension (positive tension)
        tensed_elements = self.elements.copy_and_update(
            nodes=self.nodes,
            delta_free_length=self.elements.delta_free_length,
            tension=np.array([1000.0, 1000.0])
        )
        np.testing.assert_array_equal(tensed_elements.area, [1000.0, 1000.0])
        np.testing.assert_array_equal(tensed_elements.young, [10000.0, 10000.0])
        
    def test_flexibility(self):
        """Test computation of flexibility (L/EA)."""
        # When zero tension, flexibility is computed based on type (-1 for bars, 1 for cables)
        np.testing.assert_array_equal(self.elements.type, [-1, -1]) # check that elements are bars

        # Expected flexibility = L/(E*A)
        L = np.sqrt(2.0)  # Length of each element
        E = 10000.0  # Young's modulus
        A = 2500.0   # Area
        expected_flexibility = L / (E * A)
        
        np.testing.assert_array_almost_equal(
            self.elements.flexibility,
            [expected_flexibility, expected_flexibility]
        )
        
    def test_direction_cosines(self):
        """Test computation of direction cosines."""
        # For element 0: (1,0,1)/sqrt(2)
        # For element 1: (1,0,-1)/sqrt(2)
        expected_cosines = np.array([
            [1/np.sqrt(2), 0, 1/np.sqrt(2)],
            [1/np.sqrt(2), 0, -1/np.sqrt(2)]
        ])
        np.testing.assert_array_almost_equal(self.elements.direction_cosines, expected_cosines)
        
    def test_copy_and_update(self):
        """Test copy_and_update method."""
        new_delta_free_length = np.array([0.1, 0.1])
        new_tension = np.array([1000.0, 1000.0])
        
        elements_copy = self.elements.copy_and_update(
            self.nodes,
            new_delta_free_length,
            new_tension
        )
        
        # Check immutable attributes are copied
        np.testing.assert_array_equal(elements_copy.type, self.elements.type)
        np.testing.assert_array_equal(elements_copy.end_nodes, self.elements.end_nodes)
        
        # Check mutable state is updated
        np.testing.assert_array_equal(elements_copy.delta_free_length, new_delta_free_length)
        np.testing.assert_array_equal(elements_copy.tension, new_tension)
        
    def test_copy_and_add(self):
        """Test copy_and_add method."""
        delta_free_length_inc = np.array([0.1, 0.1])
        tension_inc = np.array([1000.0, 1000.0])
        
        elements_copy = self.elements.copy_and_add(
            self.nodes,
            delta_free_length_inc,
            tension_inc
        )
        
        # Check immutable attributes are copied
        np.testing.assert_array_equal(elements_copy.type, self.elements.type)
        np.testing.assert_array_equal(elements_copy.end_nodes, self.elements.end_nodes)
        
        # Check mutable state is incremented
        np.testing.assert_array_equal(
            elements_copy.delta_free_length,
            self.elements.delta_free_length + delta_free_length_inc
        )
        np.testing.assert_array_equal(
            elements_copy.tension,
            self.elements.tension + tension_inc
        )
        
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test reshape_array_1d with wrong size
        with self.assertRaises(ValueError):
            self.elements._reshape_array_1d(np.array([1.0]), "test_array")
            
        with self.assertRaises(ValueError):
            self.elements._reshape_array_1d(np.array([1.0, 2.0, 3.0]), "test_array")
            
        # Test that reshape works with correct size but different shape
        reshaped = self.elements._reshape_array_1d(np.array([[1.0], [2.0]]), "test_array")
        np.testing.assert_array_equal(reshaped, np.array([1.0, 2.0]))
        
        # Test copy_and_update with wrong size arrays
        with self.assertRaises(ValueError):
            self.elements.copy_and_update(
                nodes=self.nodes,
                delta_free_length=np.array([1.0]),  # Wrong size
                tension=np.array([0.0, 0.0])
            )
            
        with self.assertRaises(ValueError):
            self.elements.copy_and_update(
                nodes=self.nodes,
                delta_free_length=np.array([0.0, 0.0]),
                tension=np.array([1.0, 2.0, 3.0])  # Wrong size
            )


if __name__ == '__main__':
    unittest.main()