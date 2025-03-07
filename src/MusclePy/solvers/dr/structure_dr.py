from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.solvers.dr.nodes_dr import Nodes_DR
import numpy as np


class Structure_DR(FEM_Structure):
    """
    Extension of FEM_Structure with Dynamic Relaxation specific attributes.
    
    This class adds the necessary attributes for performing Dynamic Relaxation
    analysis on a structure, specifically:
    - A_3n: Equilibrium matrix of the structure
    - global_material_stiffness_matrix: Global material stiffness matrix
    - global_geometric_stiffness_matrix: Global geometric stiffness matrix
    
    These attributes are used in the Dynamic Relaxation method as described in:
    [1] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm
    [2] Barnes, 1999, Form finding and analysis of tension structures by dynamic relaxation
    """
    
    def __init__(self, nodes: FEM_Nodes, elements: FEM_Elements):
        """
        Initialize Structure_DR, extending FEM_Structure with DR-specific attributes.
        
        Args:
            nodes: FEM_Nodes instance containing nodal data
            elements: FEM_Elements instance that must reference the same nodes instance
        """
        # Call parent class constructor
        super().__init__(nodes, elements)
        
        # Initialize DR-specific attributes
        self.A_3n = self._equilibrium_matrix(self.elements.connectivity, self.nodes.coordinates)
        self.global_material_stiffness_matrix = self._material_stiffness_matrix(self.A_3n, self.elements.flexibility)
        self.global_geometric_stiffness_matrix = self._local_to_global_stiffness_matrix(
            self._compute_local_geometric_stiffness_matrices()
        )
        
    def _equilibrium_matrix(self, connectivity_matrix, current_coordinates):
        """
        Compute the equilibrium matrix of the structure in its current state.
        
        This method uses the systematic approach described in Appendix A.4 of 
        Feron J., Latteur P., Almeida J., 2024, Static Modal Analysis, Arch Comp Meth Eng.
        
        Args:
            connectivity_matrix: (b, n) : connectivity matrix of the structure
            current_coordinates: (n, 3) : current coordinates of the nodes
        
        Returns:
            np.ndarray: (3* n, b) : equilibrium matrix of the structure (containing the free and fixed DOF)
        """
        C = connectivity_matrix

        b, n = C.shape  # number of elements, number of nodes
        
        assert current_coordinates.shape == (n, 3), "Please check the shape of the current coordinates"

        x, y, z = current_coordinates.T

        dx = C @ x
        dy = C @ y
        dz = C @ z

        current_length = np.sqrt(dx**2 + dy**2 + dz**2)

        cx = dx / current_length
        cy = dy / current_length
        cz = dz / current_length

        # Calculate equilibrium matrix
        # For each node (= one row i), if the element (= a column j) is connected to the node, 
        # then the entry (i,j) of A contains the cosinus director, else 0.
        Ax = C.T @ np.diag(cx)  # (n, b)  =  (n, b) @ (b, b)
        Ay = C.T @ np.diag(cy)
        Az = C.T @ np.diag(cz)

        A = np.zeros((3 * n, b))  
        # The Degrees Of Freedom are sorted like this [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        # Vectorized assignment - more efficient than using a loop
        A[0::3, :] = Ax  # X components for all nodes
        A[1::3, :] = Ay  # Y components for all nodes
        A[2::3, :] = Az  # Z components for all nodes

        return A

    def _material_stiffness_matrix(self, A, flexibility):
        """
        Compute the material stiffness matrix of the structure in its current state.
        
        Args:
            A: np.ndarray: (3*n, b) : equilibrium matrix of the structure.
            flexibility: np.ndarray: (b,) : flexibility vector L/EA for each element.
        
        Returns:
            np.ndarray: (3*n, 3*n) : material stiffness matrix of the structure
        """
        _3n, b = A.shape

        # Assert that sizes are compatible        
        assert flexibility.size == b, "Please check the shape of the flexibility vector"
        
        # Create diagonal matrix of stiffness values (inverse of flexibility)
        Ke = np.diag(1 / flexibility)  # EA/L in a diagonal matrix. Note that EA/L can be equal to 0 if the cable is slacked
        
        # The compatibility matrix is the transpose of the equilibrium matrix
        B = A.T  
        
        # Compute the material stiffness matrix
        Km = A @ Ke @ B  # (3*n, 3*n)
        return Km
    
    def _compute_local_geometric_stiffness_matrices(self):
        """
        Compute local geometric stiffness matrices for all elements.
        
        Returns:
            list: List of local geometric stiffness matrices, each of shape (6,6)
        """
        local_matrices = []
        
        for i in range(self.elements.count):
            # Get element properties
            n0, n1 = self.elements.end_nodes[i]
            tension = self.elements.tension[i]
            length = self.elements.length[i]
            
            # Get node coordinates
            p0 = self.nodes.coordinates[n0]
            p1 = self.nodes.coordinates[n1]
            
            # Calculate direction cosines
            dx, dy, dz = p1 - p0
            c = np.array([dx, dy, dz]) / length
            
            # Create 3x3 identity matrix
            I = np.eye(3)
            
            # Create 3x3 matrix of direction cosines products
            cc = np.outer(c, c)
            
            # Calculate the 3x3 block for geometric stiffness
            kg_block = tension / length * (I - cc)
            
            # Create the 6x6 local geometric stiffness matrix
            kg = np.zeros((6, 6))
            kg[0:3, 0:3] = kg_block
            kg[0:3, 3:6] = -kg_block
            kg[3:6, 0:3] = -kg_block
            kg[3:6, 3:6] = kg_block
            
            local_matrices.append(kg)
            
        return local_matrices
        
    def _local_to_global_stiffness_matrix(self, local_matrices: list) -> np.ndarray:
        """
        Convert list of local stiffness matrices to global stiffness matrix.
        
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
    
    def copy_and_update(self, loads: np.ndarray = None, displacements: np.ndarray = None, 
                        reactions: np.ndarray = None, delta_free_length: np.ndarray = None, 
                        tension: np.ndarray = None, resisting_forces: np.ndarray = None,
                        velocity: np.ndarray = None, mass: np.ndarray = None) -> 'Structure_DR':
        """
        Create a copy of this structure and update its state, or use the current state if None is passed.
        
        Args:
            loads: [N] - shape (nodes_count, 3) or (3*nodes_count,) - External loads
            displacements: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Support reactions
            delta_free_length: [m] - shape (elements_count,) - Change in free length
            tension: [N] - shape (elements_count,) - Element tensions
            resisting_forces: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Internal resisting forces
            velocity: [m/s] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal velocities
            mass: [kg] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal masses
            
        Returns:
            New Structure_DR with updated state
        """
        # If the current nodes are Nodes_DR, create a new Nodes_DR instance
        if isinstance(self.nodes, Nodes_DR):
            nodes_copy = self.nodes.copy_and_update(
                loads=loads,
                displacements=displacements,
                reactions=reactions,
                resisting_forces=resisting_forces,
                velocity=velocity,
                mass=mass
            )
        else:
            # Create a regular FEM_Nodes copy
            nodes_copy = self.nodes.copy_and_update(
                loads=loads,
                displacements=displacements,
                reactions=reactions,
                resisting_forces=resisting_forces
            )
            
            # Convert to Nodes_DR if velocity or mass is provided
            if velocity is not None or mass is not None:
                nodes_copy = Nodes_DR(
                    initial_coordinates=nodes_copy.initial_coordinates,
                    dof=nodes_copy.dof,
                    loads=nodes_copy.loads,
                    displacements=nodes_copy.displacements,
                    reactions=nodes_copy.reactions,
                    resisting_forces=nodes_copy.resisting_forces,
                    velocity=velocity,
                    mass=mass
                )
        
        # Create new elements with updated state
        elements_copy = self.elements.copy_and_update(
            nodes=nodes_copy,
            delta_free_length=delta_free_length,
            tension=tension
        )
        
        # Create and return new Structure_DR instance
        return Structure_DR(nodes_copy, elements_copy)
    
    def copy(self) -> 'Structure_DR':
        """
        Create a copy of this structure with the current state.
        
        Returns:
            A new Structure_DR instance with the current state
        """
        return self.copy_and_update()
