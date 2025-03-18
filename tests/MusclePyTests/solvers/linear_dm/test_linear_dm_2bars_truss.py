import unittest
import numpy as np
from MusclePy.solvers.dm.linear_dm import main_linear_displacement_method
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.femodel.pynodes import PyNodes
from MusclePy.femodel.pyelements import PyElements
from MusclePy.femodel.prestress_scenario import PrestressScenario


class TestLinearDM_2BarsTruss(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a simple 2-bar structure.
        Solution for this test can be find in Annexe A1.1.1 of J.Feron Master thesis (p103 of pdf))

        Node 1 (1,0,1)
           /\
          /  \
         /    \
        Node 0  Node 2
        (0,0,0) (2,0,0)
        """
        # Create nodes
        self.nodes = PyNodes(
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
        
        # Create elements
        self.elements = PyElements(
            nodes=self.nodes,
            type=np.array([-1, -1]),  # Two struts
            end_nodes=np.array([[0, 1], [1, 2]]),  # Element 0: 0->1, Element 1: 1->2
            area=np.array([2500.0, 2500.0]),  # 2500 mm² area
            youngs=np.array([[10000.0, 10000.0], [10000.0, 10000.0]]),  # 10000 MPa Young's modulus
            tension=np.array([0.0, 0.0])  # No initial tension
        )
        
        # Create structure
        self.structure = PyTruss(self.nodes, self.elements)

    def test_vertical_load(self):
        """Test structure response to vertical load.
        Solution for this test can be find in Annexe A1.1.1 of J.Feron Master thesis (p103 of pdf))
        """
        # Apply -100kN vertical load at node 1
        loads = np.zeros(9)  # 3 nodes * 3 DOFs
        loads[5] = -100000.0  # Node 1, Z direction
        
        # No prestress
        prestress_increment = PrestressScenario(self.structure.elements) #empty prestress increment
        
        # Solve
        result = main_linear_displacement_method(
            self.structure,
            loads,
            prestress_increment
        )
        
        # Check displacements
        displacements = result.nodes.displacements
        d1z = displacements[1, 2]  # Node 1, Z displacement
        self.assertAlmostEqual(d1z, -5.6568e-3, places=6)
        
        # Check tensions (analytical solution)
        analytic_result = loads[5]/(np.sqrt(2)) #-70711.0 N
        expected_tensions = np.array([analytic_result, analytic_result])
        np.testing.assert_allclose(result.elements.tension, expected_tensions, rtol=1e-4)
        
        # Check reactions (analytical solution)
        reactions = result.nodes.reactions.flatten()
        expected_reactions = np.array([
            50000.0, 0.0, 50000.0,  # Node 0
            0.0, 0.0, 0.0,          # Node 1 (free)
            -50000.0, 0.0, 50000.0   # Node 2
        ])
        np.testing.assert_allclose(reactions, expected_reactions, rtol=1e-3)

        # Check resisting forces
        resisting_forces = result.nodes.resisting_forces.flatten()
        expected_resisting_forces = np.array([
            50000.0, 0.0, 50000.0,  # Node 0
            0.0, 0.0, -100000.0,          # Node 1 (free)
            -50000.0, 0.0, 50000.0   # Node 2
        ])
        np.testing.assert_allclose(resisting_forces, expected_resisting_forces, rtol=1e-3)

        # Check residual: should be very small
        residual = result.nodes.residuals
        np.testing.assert_allclose(residual, np.zeros_like(residual), atol=1e-10)

        self.assertEqual(result.is_in_equilibrium(), True)


if __name__ == '__main__':
    unittest.main()
