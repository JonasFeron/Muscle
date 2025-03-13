import unittest
import numpy as np
from MusclePy.solvers.dm.nonlinear_dm import main_nonlinear_displacement_method
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements


class TestNonlinearDM_2BarsTruss(unittest.TestCase):
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
        
        # Create elements
        self.elements = FEM_Elements(
            nodes=self.nodes,
            type=np.array([-1, -1]),  # Two struts
            end_nodes=np.array([[0, 1], [1, 2]]),  # Element 0: 0->1, Element 1: 1->2
            area=np.array([2500.0, 2500.0]),  # 2500 mm² area
            youngs=np.array([[10000.0, 10000.0], [10000.0, 10000.0]]),  # 10000 MPa Young's modulus
        )
        
        # Create structure
        self.structure = FEM_Structure(self.nodes, self.elements)

    def test_vertical_load(self):
        """Test structure response to vertical load.
        Solution for this test can be find in Annexe A1.1.1 of J.Feron Master thesis (p103 of pdf))
        """
        # Apply -100kN vertical load at node 1
        loads = np.zeros(9)  # 3 nodes * 3 DOFs
        loads[5] = -100000.0  # Node 1, Z direction
        
        # Solve with nonlinear solver
        result = main_nonlinear_displacement_method(
            self.structure,
            loads,
            n_steps=100
        )
        
        # Check displacements
        displacements = result.nodes.displacements
        d1z = displacements[1, 2]  # Node 1, Z displacement
        np.testing.assert_allclose(d1z , -5.6568e-3, rtol=0.02) # 2% precision is Less precise than linear method due to equilibrium in deformed state

        # Check tensions (analytical solution)
        analytic_result = loads[5]/(np.sqrt(2)) #-70711.0 N
        expected_tensions = np.array([analytic_result, analytic_result])
        np.testing.assert_allclose(result.elements.tension, expected_tensions, rtol=0.02)
        
        # Check reactions (analytical solution)
        reactions = result.nodes.reactions.flatten()
        expected_reactions = np.array([
            50000.0, 0.0, 50000.0,  # Node 0
            0.0, 0.0, 0.0,          # Node 1 (free)
            -50000.0, 0.0, 50000.0   # Node 2
        ])
        np.testing.assert_allclose(reactions, expected_reactions, atol=500) # 1% precison, use absolute tolerance due to zero reactions

        # Check resisting forces
        resisting_forces = result.nodes.resisting_forces.flatten()
        expected_resisting_forces = np.array([
            50000.0, 0.0, 50000.0,  # Node 0
            0.0, 0.0, -100000.0,    # Node 1 (free)
            -50000.0, 0.0, 50000.0  # Node 2
        ])
        np.testing.assert_allclose(resisting_forces, expected_resisting_forces, atol=500) # 1% precison

        # self.assertEqual(result.is_in_equilibrium, True) # is_in_equilibrium will most probably be false, since the incremental newton_raphson procedure is not iterative, it will not ensure that the residual loads are null.

    def test_snap_through(self):
        """Test snap through behavior of 2-bar truss.
        Check that Snap through has occurred (cfr J.Feron Master thesis p34 of pdf)
        """
        # Create nodes for upward configuration
        nodes_up = FEM_Nodes(
            initial_coordinates=np.array([
                [0.0, 0.0, 0.0],    # Node 0: origin
                [1.0, 0.0, 0.1],    # Node 1: slightly up
                [2.0, 0.0, 0.0]     # Node 2: right
            ]),
            dof= self.nodes.dof
        )
        
        # Create elements and structure for upward configuration
        elements_up = self.elements.copy_and_update(nodes_up)
        structure_up = FEM_Structure(nodes_up, elements_up)
        
        # Create nodes for downward configuration
        nodes_down = FEM_Nodes(
            initial_coordinates=np.array([
                [0.0, 0.0, 0.0],     # Node 0: origin
                [1.0, 0.0, -0.1],    # Node 1: slightly down
                [2.0, 0.0, 0.0]      # Node 2: right
            ]),
            dof= self.nodes.dof
        )
        
        elements_down = self.elements.copy_and_update(nodes_down)
        structure_down = FEM_Structure(nodes_down, elements_down)
        
        # Apply -15kN vertical load at node 1
        loads = np.zeros(9)  # 3 nodes * 3 DOFs
        loads[5] = -15000.0  # Node 1, Z direction
        
        # Solve both configurations
        result_up = main_nonlinear_displacement_method(
            structure_up,
            loads,
            n_steps=100
        )
        
        result_down = main_nonlinear_displacement_method(
            structure_down,
            loads,
            n_steps=100
        )
        
        # Both configurations should converge to the same solution after snapthrough occured
        structure_up_coord1z = result_up.nodes.coordinates[1,2]
        structure_down_coord1z = result_down.nodes.coordinates[1,2]
        np.testing.assert_allclose(structure_up_coord1z, structure_down_coord1z, rtol=2e-2)
        np.testing.assert_allclose(result_up.elements.tension, result_down.elements.tension, rtol=2e-2)


if __name__ == '__main__':
    unittest.main()
