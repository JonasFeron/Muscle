from MusclePy.solvers.linear_dm.elements_linear_dm import Elements_Linear_DM
from MusclePy.femodel.fem_nodes import FEM_Nodes
import numpy as np


class Structure_Linear_DM(Structure_State):
    def __init__(self, nodes=None, elements=None, applied=None, initial_nodes_results=None, initial_elements_results=None):
        """Initialize Structure_State_4Linear_DM, extending Structure_State with stiffness matrices attributes.
        
        Args:
            Same arguments as Structure_State
        """
        # Call parent class constructor
        self.nodes = FEM_Nodes(nodes,applied,initial_nodes_results)  
        self.elements = Elements_Linear_DM(elements,self.nodes,applied,initial_elements_results) 

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
        


