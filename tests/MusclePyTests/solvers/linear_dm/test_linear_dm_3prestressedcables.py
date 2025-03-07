import unittest
import numpy as np
from MusclePy.solvers.dm.linear.method import LinearDisplacementMethod
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements

class TestLinearDM_3PrestressedCables(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a tight rope structure with vertical cable.
        Structure layout:
                    Node 3 (0,0,1)
                    |
                    | (cable 3)
                    |
        Node 0----Node 1----Node 2
       (-2,0,0)   (0,0,0)    (2,0,0)         
             cable1    cable2
        """
        # Create nodes
        self.nodes = FEM_Nodes(
            initial_coordinates=np.array([
                [-2.0, 0.0, 0.0],  # Node 0: left support
                [0.0, 0.0, 0.0],   # Node 1: middle point
                [2.0, 0.0, 0.0],   # Node 2: right support
                [0.0, 0.0, 1.0]    # Node 3: top point
            ]),
            dof=np.array([
                [False, False, False],  # Node 0: fixed
                [True, False, True],    # Node 1: free in x,z
                [False, False, False],  # Node 2: fixed
                [False, False, False]   # Node 3: fixed
            ])
        )
        
        # Create elements (all cables)
        type=np.array([1, 1, 1])  # All elements are cables (type=1)
        areas = np.ones((3,2)) * 50.26 #[mm²]
        youngs = np.ones((3,2)) * 70e3 #70 GPa Young's modulus
        youngs[:, 0] = 0 #tension only elements -> no stiffness in compression

        self.elements = FEM_Elements(
            nodes=self.nodes,
            type=type,
            end_nodes=np.array([[0, 1], [1, 2], [1, 3]]),  # Define connectivity
            areas= areas, 
            youngs=youngs, 
            delta_free_length=np.array([0.0, 0.0, 0.0]),  # No initial prestress
            tension=np.array([0.0, 0.0, 0.0])
        )
        
        # Create structure
        self.structure = FEM_Structure(self.nodes, self.elements)

    def test_equivalent_prestress_loads(self):
        """Test the equivalent_prestress_loads function with the cable structure."""
        
        # Apply prestress through shortening first cable only
        delta_free_length_increment = np.array([-0.007984, 0.0, 0.0])

        prestressed_elements = self.structure.elements.copy_and_add(self.structure.nodes, delta_free_length_increment,None)

        # Expected prestress force magnitude in cable 1: EA/L * dl
        # EA = 50.26 * 70e3 = 3518.2 kN
        # L = 2.0-0.007984 m (free length of cable 1)
        # -> Expected force ≈ 14100.945 N in cable 1 assuming all nodes are fixed
        expected_free_length = np.array([2.0, 2.0, 1.0]) + delta_free_length_increment
        np.testing.assert_allclose(prestressed_elements.current_free_length, expected_free_length, atol=1e-6)


        prestress, loads = LinearDisplacementMethod._equivalent_prestress_loads(prestressed_elements, delta_free_length_increment)
        
        # Test 1: Check prestress forces
        expected_prestress = np.array([14100.945, 0.0, 0.0])
        np.testing.assert_allclose(prestress, expected_prestress, rtol=1e-4)
        
        # Test 2: Sum of forces should be zero

        total_force = np.sum(loads, axis=0)
        np.testing.assert_allclose(total_force, [0, 0, 0], atol=1e-10)
        
        # Test 3: Check force directions and magnitudes
        # Node 0 (left support) should have force pointing right
        # Node 1 (middle) should have force pointing left
        node0_force = loads[0]
        node1_force = loads[1]
        
        self.assertGreater(node0_force[0], 0)  # loads points right at left support
        self.assertLess(node1_force[0], 0)     # loads points left at middle node
        self.assertAlmostEqual(abs(node0_force[0]), prestress[0], places=3)  # Force magnitude matches prestress

    def test_prestress(self):
        """Test prestress through free length changes in cable structure."""
        # No external loads
        loads_increment = np.zeros(12)  # 4 nodes * 3 DOFs
        
        # Apply prestress through free length change in first cable only
        delta_free_length_increment = np.array([-0.007984, 0.0, 0.0])  # ~8mm shortening in first cable
        
        # Expected prestress force magnitude in cables 1&2: EA/L * dl
        # EA = 50.26 * 70e3 = 3518.2 kN
        # L = 4.0 -0.007984  m (free length of cables 1 and 2)
        # -> Expected force ≈ 7036.37 N in both cables

        # Solve
        result = LinearDisplacementMethod.apply_loads_and_prestress_increments(
            self.structure,
            loads_increment,
            delta_free_length_increment
        )
        
        # Check displacements
        displacements = result.nodes.displacements
        self.assertAlmostEqual(displacements[1, 0], -0.004, places=3)  # Node 1 should move left ~4mm
        
        # Check tensions - first two cables should have equal tension due to symmetry
        tensions = result.elements.tension
        self.assertGreater(tensions[0], 0)  # First cable in tension
        self.assertGreater(tensions[1], 0)  # Second cable in tension
        self.assertAlmostEqual(tensions[0], 7036.37, places=2)  # Match analytical solution
        self.assertAlmostEqual(tensions[0], tensions[1], places=4)  # Symmetric tension
        self.assertLess(abs(tensions[2]), 1.0)  # Vertical cable should have negligible tension

    def test_cable_slackening(self):
        """Test cable slackening:
        Apply small upward load on middle node to obtain small compression in cable3
        """
        self.assertEqual(self.structure.elements.type[2],1) #element 3 is a cable (type =1)
        self.assertEqual(self.structure.elements.youngs[2,0], 0) #the young modulus in compression is equal to 0
        self.assertGreater(self.structure.elements.youngs[2,1], 0) #the young modulus in tension is higher than 0

        self.assertEqual(self.structure.elements.tension[2], 0) #the current tension in the cable is null
        self.assertGreater(self.structure.elements.young[2], 0) #when 0 force, choose the young modulus in tension

        loads = np.zeros((4,3))
        loads[1,2] = 0.1  # 0.1N upward at node 1
        result = LinearDisplacementMethod.apply_loads_and_prestress_increments(
            self.structure,
            loads,
            np.zeros(3)  # no free length changes
        )
        
        #  in step 1: Verify upward movement, compression in cable 3, and 0 stiffness
        self.assertGreater(result.nodes.displacements[1,2], 0)
        self.assertEqual(result.elements.tension[2], -0.1)
        self.assertEqual(result.elements.young[2], 0) #the young modulus in compression

        stiffness = 1/result.elements.flexibility[2]
        self.assertAlmostEqual(result.elements.young[2], 0, places=5) #the stiffness in compression

        #a new application of an upward load will lead to 0 compression force
        


if __name__ == '__main__':
    unittest.main()
