from MusclePy.solvers.linear_dm.elements_linear_dm import Elements_Linear_DM
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
import numpy as np


class Structure_Linear_DM(FEM_Structure):
    def __init__(self, nodes: FEM_Nodes, elements: Elements_Linear_DM):
        """Initialize Structure_Linear_DM, extending FEM_Structure with stiffness matrices.
        
        Args:
            nodes: FEM_Nodes instance containing nodal data
            elements: Elements_Linear_DM instance that must reference the same nodes instance
        """
        # Call parent class constructor
        super().__init__(nodes, elements)
        
        # Initialize stiffness matrices attributes
        self.global_material_stiffness_matrix = None  # [N/m] - shape (3*nodes.count, 3*nodes.count)
        self.global_geometric_stiffness_matrix = None  # [N/m] - shape (3*nodes.count, 3*nodes.count)

        self._compute_stiffness_matrices()

    def _compute_stiffness_matrices(self):
        """Compute all global stiffness matrices for the structure.
        
        This method computes:
        1. Global material stiffness matrix
        2. Global geometric stiffness matrix
        """
  
        # Convert local matrices to global matrices
        self.global_material_stiffness_matrix = self._local_to_global_stiffness_matrix(
            self.elements.local_material_stiffness_matrices
        )
        self.global_geometric_stiffness_matrix = self._local_to_global_stiffness_matrix(
            self.elements.local_geometric_stiffness_matrices
        )

       
    def _local_to_global_stiffness_matrix(self, local_matrices: list) -> np.ndarray:
        """Convert list of local stiffness matrices to global stiffness matrix.
        
        Args:
            local_matrices: List of local stiffness matrices, each of shape (6,6)
            
        Returns:
            Global stiffness matrix of shape (3*nodes.count, 3*nodes.count)
        """
        if self.elements.count == 0 or not local_matrices:
            return np.array([], dtype=float)
            
        K = np.zeros((3 * self.nodes.count, 3 * self.nodes.count))
        
        # Assembly of local matrices into global one
        for i in range(self.elements.count):
            n0, n1 = self.elements.end_nodes[i]
            k = local_matrices[i]
            
            # Global indices for the 6 DOFs of the element
            idx = np.array([3*n0, 3*n0+1, 3*n0+2, 3*n1, 3*n1+1, 3*n1+2], dtype=int)
            
            # Add local stiffness contributions to global matrix
            for j in range(6):
                for l in range(6):
                    K[idx[j], idx[l]] += k[j, l]
                    
        return K

    def copy_and_update(self, loads: np.ndarray = None, displacements: np.ndarray = None, reactions: np.ndarray = None,
                       delta_free_length: np.ndarray = None, tension: np.ndarray = None, resisting_forces: np.ndarray = None) -> 'Structure_Linear_DM':
        """Create a copy of this structure and update its state, or use the current state if None is passed."""
        # Create new nodes with updated state
        nodes_copy = self._nodes.copy_and_update(loads, displacements, reactions, resisting_forces)
        
        # Create new elements with updated state, referencing the new nodes
        elements_copy = self._elements.copy_and_update(nodes_copy, delta_free_length, tension)
        
        return Structure_Linear_DM(nodes_copy, elements_copy)
        
    def copy_and_add(self, loads_increment: np.ndarray = None, displacements_increment: np.ndarray = None, 
                     reactions_increment: np.ndarray = None, delta_free_length_increment: np.ndarray = None,
                     tension_increment: np.ndarray = None, resisting_forces_increment: np.ndarray = None) -> 'Structure_Linear_DM':
        """Create a copy of the structure and add increments to its state.
        
        Args:
            loads_increment: [N] - size: 3*nodes.count - Loads increment to add
            displacements_increment: [m] - size: 3*nodes.count - Displacements increment to add
            reactions_increment: [N] - size: 3*nodes.count - Reactions increment to add
            delta_free_length_increment: [m] - size: elements.count - Free length increment to add
            tension_increment: [N] - size: elements.count - Tension increment to add
            resisting_forces_increment: [N] - size: 3*nodes.count - Resisting forces increment to add
            
        Returns:
            New Structure_Linear_DM with incremented state
        """
        # Create new nodes with incremented state
        new_nodes = self.nodes.copy_and_add(
            loads_increment=loads_increment,
            displacements_increment=displacements_increment,
            reactions_increment=reactions_increment,
            resisting_forces_increment=resisting_forces_increment
        )
        
        # Create new elements with incremented state, referencing the new nodes
        new_elements = self.elements.copy_and_add(
            nodes=new_nodes,
            delta_free_length_increment=delta_free_length_increment,
            tension_increment=tension_increment
        )
        
        return Structure_Linear_DM(new_nodes, new_elements)

    def copy(self) -> 'Structure_Linear_DM':
        """Create a copy of this structure with the current state.
        
        Returns:
            A new Structure_Linear_DM instance with copied nodes and elements
        """
        # Create new nodes with current state
        nodes_copy = self._nodes.copy()
        
        # Create new elements with current state, referencing the new nodes
        elements_copy = self._elements.copy(nodes_copy)
        
        return Structure_Linear_DM(nodes_copy, elements_copy)

    def save_as_FEM_Structure(self) -> FEM_Structure:
        """Return a FEM_Structure with the current state of this Structure_Linear_DM.
        
        Returns:
            FEM_Structure: A new FEM_Structure instance with the current state
        """
        return FEM_Structure(
            nodes=self._nodes,
            elements=self._elements
        )
