from MusclePy.femodel.fem_nodes  import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.utils.matrix_calculations import compute_equilibrium_matrix, compute_global_material_stiffness_matrix
import numpy as np


class Structure_SVD(FEM_Structure):
    def __init__(self, nodes: FEM_Nodes, elements: FEM_Elements):
        """Initialize Structure_SVD, extending FEM_Structure with equilibrium matrix, and singular value decomposition method.
        
        Args:
            nodes: FEM_Nodes instance containing nodal data
            elements: FEM_Elements instance that must reference the same nodes instance
        """
        # Call parent class constructor
        super().__init__(nodes, elements)

        # Initialize attributes using utility functions
        self.A_3n = compute_equilibrium_matrix(self.elements.connectivity, self.nodes.coordinates)
        self.global_material_stiffness_matrix = compute_global_material_stiffness_matrix(self.A_3n, self.elements.flexibility)


    @property
    def A(self):
        """
        Returns:
            np.ndarray: (3* nodes_count - fixations_count, elements_count) : equilibrium matrix of the structure (containing the free DOF only)
        """
        return self.A_3n[self.nodes.dof.reshape((-1,)),:] 

    @property
    def Afix(self):
        """
        Returns:
            np.ndarray: (fixations_count, elements_count) : equilibrium matrix of the structure (containing the fixed DOF only)
        """
        return self.A_3n[~self.nodes.dof.reshape((-1,)),:] 
