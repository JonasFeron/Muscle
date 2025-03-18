import unittest
import numpy as np
import os
import sys
from MusclePy.femodel.pynodes import PyNodes


class TestPyNodes(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a simple 3-node structure.
        Node 1 (1,0,1)
           /\
          /  \
         /    \
        Node 0  Node 2
        (0,0,0) (2,0,0)
        """
        self.initial_coordinates = np.array([
            [0.0, 0.0, 0.0],  # Node 0: origin
            [1.0, 0.0, 1.0],  # Node 1: top
            [2.0, 0.0, 0.0]   # Node 2: right
        ])
        self.dof = np.array([
            [False, False, False],  # Node 0: fixed
            [True, False, True],    # Node 1: free in x,z
            [False, False, False]   # Node 2: fixed
        ])
        self.loads = np.array([
            [0.0, 0.0, 0.0],    # Node 0: no load
            [100.0, 0.0, 50.0], # Node 1: load in x,z
            [0.0, 0.0, 0.0]     # Node 2: no load
        ])
        self.nodes = PyNodes(
            initial_coordinates=self.initial_coordinates,
            dof=self.dof,
            loads=self.loads
        )

    def test_initialization(self):
        """Test proper initialization of PyNodes."""
        # Test basic properties
        self.assertEqual(self.nodes.count, 3)
        self.assertEqual(self.nodes.fixations_count, 7)  # 7 fixed DOFs

        # Test array shapes and values
        np.testing.assert_array_equal(self.nodes.initial_coordinates, self.initial_coordinates)
        np.testing.assert_array_equal(self.nodes.coordinates, self.initial_coordinates)  # No displacements yet
        np.testing.assert_array_equal(self.nodes.dof, self.dof)
        np.testing.assert_array_equal(self.nodes.loads, self.loads)

        # Test default zero arrays
        np.testing.assert_array_equal(self.nodes.displacements, np.zeros((3, 3)))
        np.testing.assert_array_equal(self.nodes.reactions, np.zeros((3, 3)))
        np.testing.assert_array_equal(self.nodes.resisting_forces, np.zeros((3, 3)))

    def test_coordinates_update(self):
        """Test that coordinates update correctly with displacements."""
        displacements = np.array([
            [0.0, 0.0, 0.0],     # Node 0: fixed
            [0.1, 0.0, -0.2],    # Node 1: moves
            [0.0, 0.0, 0.0]      # Node 2: fixed
        ])
        nodes = PyNodes(
            initial_coordinates=self.initial_coordinates,
            dof=self.dof,
            displacements=displacements
        )
        expected_coordinates = self.initial_coordinates + displacements
        np.testing.assert_array_equal(nodes.coordinates, expected_coordinates)

    def test_residual_computation(self):
        """Test computation of residual forces."""
        resisting_forces = np.array([
            [0.0, 0.0, 0.0],      # Node 0
            [80.0, 0.0, 30.0],    # Node 1
            [0.0, 0.0, 0.0]       # Node 2
        ])
        nodes = PyNodes(
            initial_coordinates=self.initial_coordinates,
            dof=self.dof,
            loads=self.loads,
            resisting_forces=resisting_forces
        )
        expected_residual = self.loads - resisting_forces
        np.testing.assert_array_equal(nodes.residuals, expected_residual)

    def test_copy_and_update(self):
        """Test copy_and_update method."""
        new_loads = np.array([
            [0.0, 0.0, 0.0],      # Node 0
            [200.0, 0.0, 100.0],  # Node 1
            [0.0, 0.0, 0.0]       # Node 2
        ])
        new_displacements = np.array([
            [0.0, 0.0, 0.0],    # Node 0
            [0.2, 0.0, -0.1],   # Node 1
            [0.0, 0.0, 0.0]     # Node 2
        ])
        new_reactions = np.array([
            [50.0, 0.0, 25.0],  # Node 0
            [0.0, 0.0, 0.0],    # Node 1
            [50.0, 0.0, 25.0]   # Node 2
        ])
        new_resisting_forces = np.array([
            [0.0, 0.0, 0.0],     # Node 0
            [150.0, 0.0, 75.0],  # Node 1
            [0.0, 0.0, 0.0]      # Node 2
        ])

        nodes_copy = self.nodes.copy_and_update(
            new_loads,
            new_displacements,
            new_reactions,
            new_resisting_forces
        )

        # Check immutable attributes are copied
        np.testing.assert_array_equal(nodes_copy.initial_coordinates, self.initial_coordinates)
        np.testing.assert_array_equal(nodes_copy.dof, self.dof)

        # Check mutable state is updated
        np.testing.assert_array_equal(nodes_copy.loads, new_loads)
        np.testing.assert_array_equal(nodes_copy.displacements, new_displacements)
        np.testing.assert_array_equal(nodes_copy.reactions, new_reactions)
        np.testing.assert_array_equal(nodes_copy.resisting_forces, new_resisting_forces)

    def test_copy_and_add(self):
        """Test copy_and_add method."""
        loads_increment = np.array([
            [0.0, 0.0, 0.0],     # Node 0
            [50.0, 0.0, 25.0],   # Node 1
            [0.0, 0.0, 0.0]      # Node 2
        ])
        displacements_increment = np.array([
            [0.0, 0.0, 0.0],    # Node 0
            [0.1, 0.0, -0.1],   # Node 1
            [0.0, 0.0, 0.0]     # Node 2
        ])
        reactions_increment = np.array([
            [25.0, 0.0, 12.5],  # Node 0
            [0.0, 0.0, 0.0],    # Node 1
            [25.0, 0.0, 12.5]   # Node 2
        ])
        resisting_forces_increment = np.array([
            [0.0, 0.0, 0.0],     # Node 0
            [40.0, 0.0, 20.0],   # Node 1
            [0.0, 0.0, 0.0]      # Node 2
        ])

        nodes_copy = self.nodes.copy_and_add(
            loads_increment,
            displacements_increment,
            reactions_increment,
            resisting_forces_increment
        )

        # Check immutable attributes are copied
        np.testing.assert_array_equal(nodes_copy.initial_coordinates, self.initial_coordinates)
        np.testing.assert_array_equal(nodes_copy.dof, self.dof)

        # Check mutable state is incremented
        np.testing.assert_array_equal(nodes_copy.loads, self.loads + loads_increment)
        np.testing.assert_array_equal(nodes_copy.displacements, displacements_increment)  # Was zero
        np.testing.assert_array_equal(nodes_copy.reactions, reactions_increment)  # Was zero
        np.testing.assert_array_equal(nodes_copy.resisting_forces, resisting_forces_increment)  # Was zero

    def test_error_handling(self):
        """Test error handling for invalid inputs."""
        # Test wrong shape for initial_coordinates
        with self.assertRaises(ValueError):
            PyNodes(initial_coordinates=np.array([[0.0, 0.0]]))  # Missing z coordinate

        # Test wrong shape for dof
        with self.assertRaises(ValueError):
            PyNodes(
                initial_coordinates=self.initial_coordinates,
                dof=np.array([True, False, True])  # Wrong shape
            )

        # Test wrong shape for loads
        with self.assertRaises(ValueError):
            PyNodes(
                initial_coordinates=self.initial_coordinates,
                dof=self.dof,
                loads=np.array([[0.0, 0.0]])  # Wrong shape
            )

        # Test wrong shape for copy_and_update
        with self.assertRaises(ValueError):
            self.nodes.copy_and_update(
                loads=np.array([0.0, 0.0]),  # Wrong shape
                displacements=np.zeros((3, 3)),
                reactions=np.zeros((3, 3)),
                resisting_forces=np.zeros((3, 3))
            )

    def test_check_and_reshape_array(self):
        """Test the _check_and_reshape_array method for various input cases."""
        nodes = PyNodes(initial_coordinates=self.initial_coordinates)
        
        # Test None input
        result = nodes._check_and_reshape_array(None, "test")
        np.testing.assert_array_equal(result, np.zeros((3, 3)))
        
        # Test correct shape input
        input_array = np.ones((3, 3))
        result = nodes._check_and_reshape_array(input_array, "test")
        np.testing.assert_array_equal(result, input_array)
        
        # Test 1D input that can be reshaped
        input_array = np.ones(9)
        result = nodes._check_and_reshape_array(input_array, "test")
        np.testing.assert_array_equal(result, np.ones((3, 3)))
        
        # Test C# bool array
        bool_array = [[True, False, True], [False, True, False], [True, True, False]]
        result = nodes._check_and_reshape_array(bool_array, "dof")
        self.assertEqual(result.dtype, np.bool_)
        np.testing.assert_array_equal(result, np.array(bool_array))
        
        # Test wrong shape input
        with self.assertRaises(ValueError):
            nodes._check_and_reshape_array(np.ones(4), "test")


if __name__ == '__main__':
    unittest.main()
