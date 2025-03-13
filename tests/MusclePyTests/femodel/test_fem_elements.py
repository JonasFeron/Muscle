import unittest
import os
import sys
import numpy as np
from MusclePy import femodel



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
        self.nodes = femodel.FEM_Nodes(
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
        self.elements = femodel.FEM_Elements(
            nodes=self.nodes,
            type=np.array([-1, -1]),  # Two struts
            end_nodes=np.array([[0, 1], [1, 2]]),  # Element 0: 0->1, Element 1: 1->2
            area=np.array([2500.0, 2500.0]),  # Cross-section area
            youngs=np.array([[10000.0, 5000.0], [10000.0, 5000.0]]),  # Same Young's modulus [[compression, tension], [compression, tension],...]
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
        
    def test_current_young_tension(self):
        """Test computation of current properties based on tension state."""

        # if node 1 moves upwards, elements elongate and are in tension
        displacement = np.array([
            [0.0, 0.0, 0.0],  # Node 0: origin
            [0.0, 0.0, 0.1],  # Node 1: top
            [0.0, 0.0, 0.0]  # Node 2: right
        ])
        moved_nodes = self.nodes.copy_and_add(
            displacements_increment = displacement
        )
        
        # Test with tension (positive tension)
        tensed_elements = self.elements.copy_and_update(
            nodes=moved_nodes
        )
        np.testing.assert_array_equal(tensed_elements.young, [5000.0, 5000.0])

    def test_current_young_compression(self):
        """Test computation of current properties based on tension state."""

        # if node 1 moves downwards, elements shorten and are in compression
        displacement = np.array([
            [0.0, 0.0, 0.0],  # Node 0: origin
            [0.0, 0.0, -0.1],  # Node 1: top
            [0.0, 0.0, 0.0]  # Node 2: right
        ])
        moved_nodes = self.nodes.copy_and_add(
            displacements_increment=displacement
        )

        # Test with tension (positive tension)
        compressed_elements = self.elements.copy_and_update(
            nodes=moved_nodes
        )
        np.testing.assert_array_equal(compressed_elements.young, [10000.0, 10000.0])
        
    def test_current_flexibility(self):
        """Test computation of flexibility (L/EA)."""
        # When zero tension, flexibility is computed based on maximum young modulus.

        # Expected flexibility = L/(E*A)
        L = np.sqrt(2.0)  # Length of each element
        E = 10000.0  # maximum Young's modulus
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
        new_free_length_variation = np.array([0.1, 0.1])
        new_tension = np.array([1000.0, 1000.0])
        
        elements_copy = self.elements.copy_and_update(
            self.nodes,
            new_free_length_variation,
            new_tension
        )
        
        # Check immutable attributes are copied
        np.testing.assert_array_equal(elements_copy.type, self.elements.type)
        np.testing.assert_array_equal(elements_copy.end_nodes, self.elements.end_nodes)
        
        # Check mutable state is updated
        np.testing.assert_array_equal(elements_copy.free_length_variation, new_free_length_variation)
        np.testing.assert_array_equal(elements_copy.tension, new_tension)
        
    def test_copy_and_add(self):
        """Test copy_and_add method."""
        free_length_variation = np.array([0.1, 0.1])
        tension_inc = np.array([1000.0, 1000.0])
        
        elements_copy = self.elements.copy_and_add(
            self.nodes,
            free_length_variation,
            tension_inc
        )
        
        # Check immutable attributes are copied
        np.testing.assert_array_equal(elements_copy.type, self.elements.type)
        np.testing.assert_array_equal(elements_copy.end_nodes, self.elements.end_nodes)
        
        # Check mutable state is incremented
        np.testing.assert_array_equal(
            elements_copy.free_length_variation,
            self.elements.free_length_variation + free_length_variation
        )
        np.testing.assert_array_equal(
            elements_copy.tension,
            self.elements.tension + tension_inc
        )
        
    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test wrong shape input
        with self.assertRaises(ValueError):
            self.elements._check_and_reshape_array(np.array([1.0]), "test")
            
        # Test wrong size input
        with self.assertRaises(ValueError):
            self.elements._check_and_reshape_array(np.array([1.0, 2.0, 3.0]), "test")
            
        # Test 1D input that can be reshaped
        result = self.elements._check_and_reshape_array(np.array([1.0, 2.0]), "test")
        np.testing.assert_array_equal(result, np.array([1.0, 2.0]))
        
        # Test 2D input with shape_suffix
        result = self.elements._check_and_reshape_array(np.array([[1.0, 2.0], [3.0, 4.0]]), "areas", shape_suffix=2)
        np.testing.assert_array_equal(result, np.array([[1.0, 2.0], [3.0, 4.0]]))
        
        # Test C# array conversion
        int_array = [[-1], [-1]]  # C# array for element types
        result = self.elements._check_and_reshape_array(int_array, "type")
        self.assertEqual(result.dtype, np.int_)
        np.testing.assert_array_equal(result, np.array([-1, -1]))
        
        # Test copy_and_update with wrong size arrays
        with self.assertRaises(ValueError):
            self.elements.copy_and_update(
                nodes=self.nodes,
                free_length_variation=np.array([1.0]),  # Wrong size
                tension=np.array([0.0, 0.0])
            )
            
        with self.assertRaises(ValueError):
            self.elements.copy_and_update(
                nodes=self.nodes,
                free_length_variation=np.array([0.0, 0.0]),
                tension=np.array([1.0, 2.0, 3.0])  # Wrong size
            )


if __name__ == '__main__':
    unittest.main()