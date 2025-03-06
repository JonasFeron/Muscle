from MusclePy.femodel.fem_nodes  import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_structure import FEM_Structure
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

        self.A_3n = np.zeros((3 * self.nodes.count, self.elements.count)) # equilibrium matrix of the structure (containing the free and fixed DOF)
        self.A_3n = self._equilibrium_matrix(self.elements.connectivity, self.nodes.coordinates)

        self.global_material_stiffness_matrix = np.zeros((3 * self.nodes.count, 3 * self.nodes.count))
        self.global_material_stiffness_matrix = self._material_stiffness_matrix(self.A_3n, self.elements.flexibility)


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

    def _equilibrium_matrix(self, connectivity_matrix, current_coordinates):
        """ Compute the equilibrium matrix of the structure in its current state, using the systematic approach described in Appendix A.4 of Feron J., Latteur P., Almeida J., 2024, Static Modal Analysis, Arch Comp Meth Eng.
        
        Args:
            connectivity_matrix: (b, n) : connectivity matrix of the structure
            current_coordinates: (n, 3) : current coordinates of the nodes
        
        Returns:
            np.ndarray: (3* n, b) : equilibrium matrix of the structure (containing the free and fixed DOF)
        """
        C = connectivity_matrix

        b,n = C.shape # number of elements, number of nodes
        
        assert current_coordinates.shape == (n, 3), "Please check the shape of the current coordinates"

        x, y, z = current_coordinates.T

        dx = C @ x
        dy = C @ y
        dz = C @ z

        current_length = np.sqrt(dx**2 + dy**2 + dz**2)

        cx = dx / current_length
        cy = dy / current_length
        cz = dz / current_length

        # 2) calculate equilibrium matrix
        # for each node (= one row i), if the element (= a column j) is connected to the node, then the entry (i,j)of A contains the cosinus director, else 0.
        Ax = C.T @ np.diag(cx)  # (n, b)  =  (n, b) @ (b, b)
        Ay = C.T @ np.diag(cy)
        Az = C.T @ np.diag(cz)

        A = np.zeros((3 * n, b))  
        # the Degrees Of Freedom are sorted like this [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        # Vectorized assignment - more efficient than using a loop
        A[0::3, :] = Ax  # X components for all nodes
        A[1::3, :] = Ay  # Y components for all nodes
        A[2::3, :] = Az  # Z components for all nodes

        return A

    def _material_stiffness_matrix(self, A, flexibility):
        """
        Compute the material stiffness matrix of the structure in its current state given the equilibrium matrix and the flexibilities

        Args:
            A: np.ndarray, optional: (3*n, b) : equilibrium matrix of the structure.
            flexibility: np.ndarray, optional: (b,) : flexibility vector L/EA for each element.
        
        Returns:
            np.ndarray: (3*n, 3*n) : material stiffness matrix of the structure
        """

        _3n, b = A.shape

        #assert that sizes are compatible        
        assert flexibility.size == b, "Please check the shape of the flexibility vector"
        
        # Create diagonal matrix of stiffness values (inverse of flexibility)
        Ke = np.diag(1 / flexibility)  # EA/L in a diagonal matrix. Note that EA/L can be equal to 0 if the cable is slacked
        
        # The compatibility matrix is the transpose of the equilibrium matrix
        B = A.T  
        
        # Compute the material stiffness matrix
        Km = A @ Ke @ B  # (3*n, 3*n)
        return Km
