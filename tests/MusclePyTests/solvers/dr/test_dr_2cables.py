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


class TestDR_2Cables(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures with a 2-cable structure with 1 mechanism.
        Structure layout:

        Node 0---------Node 1---------Node 2
       (-2,0,0)      (0,0,0.0)       (2,0,0)
                cable1        cable2

        Node 1 is free to move in x and z directions.
        The structure has a slight initial displacement in the z direction at Node 1.
        """
        # Create nodes with initial displacement at node 1
        self.nodes = FEM_Nodes(
            initial_coordinates=np.array([
                [-2.0, 0.0, 0.0],  # Node 0: left support
                [0.0, 0.0, 0.0],   # Node 1: free to move
                [2.0, 0.0, 0.0]    # Node 2: right support
            ]),
            dof=np.array([
                [False, False, False],  # Node 0: fixed
                [True, False, True],    # Node 1: free in x,z
                [False, False, False]   # Node 2: fixed
            ]) 
        )
        
        # Create elements with prestress
        cable_area = np.pi * (8 / 2) ** 2  # 8mm diameter cable area in mm²
        self.cable_area = cable_area

        self.elements = FEM_Elements(
            nodes=self.nodes,
            type=np.array([1, 1]),  # Two cables
            end_nodes=np.array([[0, 1], [1, 2]]),  # Element 0: 0->1, Element 1: 1->2
            area=np.array([cable_area, cable_area]),  # 50.26 mm² area
            youngs=np.array([[70000.0, 70000.0], [70000.0, 70000.0]]),  # 70000 MPa Young's modulus
        )
        
        # Create structure
        self.structure = FEM_Structure(self.nodes, self.elements)

        # Configure solver
        self.config = DRconfig(
            zero_residual_rtol=1e-6,
            zero_residual_atol=1e-6,
            max_time_step=100,
            max_ke_reset= 20
        )

    def test_oscillating_cables_equilibrium(self):
        """Test a 2-cable structure oscillating around equilibrium position with prestress.
        The test initializes the structure with a vertical displacement at the middle node
        and lets it oscillate to find equilibrium.
        """
                
        # impose initial displacements, like you would when playing guitar
        displacements=np.array([
                [0.0, 0.0, 0.0],  # Node 0: 
                [0.0, 0.0, 0.1],   # Node 1: middle point with initial displacement in z
                [0.0, 0.0, 0.0]    # Node 2: 
            ])

        disturbed_structure = self.structure.copy_and_add(displacements_increment=displacements)


        # No external loads
        loads = np.zeros((3, 3))  # 3 nodes * 3 DOFs

        # Apply prestress
        delta_free_length=np.array([-0.001, -0.001])  # Slightly shorter than initial free length (calculated from initial coordinates) to create prestress


        # Solve with dynamic relaxation
        result = main_dynamic_relaxation(
            structure=disturbed_structure,
            loads_increment=loads,
            free_length_variation=delta_free_length,
            config=self.config
        )

        # Verify the solver converged within the maximum number of steps
        self.assertLess(self.config.n_time_step, self.config.max_time_step)
        self.assertLess(self.config.n_ke_reset, self.config.max_ke_reset)
        
        # Expected tension: T = E*A*ΔL/L = 70000*50.26*0.001/1.999
        expected_tension = 70000 * self.cable_area * 0.001 / 1.999 * np.ones(2)
        np.testing.assert_allclose(result.elements.tension, expected_tension, atol=1e-4)
        
        # Check final node position (should be at equilibrium with z=0)
        np.testing.assert_allclose(result.nodes.coordinates[1, 2], 0.0, atol=1e-6)
        


    def test_2cables_loading(self):
        """Test the 2-cable structure by loading from an unprestressed initial state.
        The test verifies the final tensions and node positions against analytical solutions.
        """
        # No prestress
        delta_free_length=np.array([0.0, 0.0])  

        # External loads
        loads = np.zeros((3, 3))  # 3 nodes * 3 DOFs
        loads[1, 2] = 888.808  # [N] vertical load at Node 1
        
        # Solve with dynamic relaxation
        result = main_dynamic_relaxation(
            structure=self.structure,
            loads_increment=loads,
            free_length_variation=delta_free_length,
            config=self.config
        )


        expected_resisting_force = 888.808 # N
        np.testing.assert_allclose(result.nodes.resisting_forces[1,2], expected_resisting_force, atol=0.001)

        expected_vertical_reactions = np.array([-444.404, -444.404])  # N
        np.testing.assert_allclose(result.nodes.reactions[[0,2],2], expected_vertical_reactions, atol=0.001)

        # Verify the solver converged within the maximum number of steps
        self.assertLess(self.config.n_time_step, self.config.max_time_step)
        self.assertLess(self.config.n_ke_reset, self.config.max_ke_reset)

        # Expected tensions from analytical solution
        expected_tensions = np.array([7037.17, 7037.17])  # [N] (yielding stress = 140 MPa) * (cable area = 50.26 mm²)
        np.testing.assert_allclose(result.elements.tension, expected_tensions, atol=0.01)

        # Expected final coordinates from analytical solution
        expected_node3_z = 0.126554  # m
        np.testing.assert_allclose(result.nodes.coordinates[1, 2], expected_node3_z, atol=1e-6)





if __name__ == '__main__':
    unittest.main()
