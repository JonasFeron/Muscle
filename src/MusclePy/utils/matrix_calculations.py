"""
Matrix calculation utilities for structural analysis.

This module provides common matrix calculation functions used across different solvers
in the MusclePy package, including equilibrium matrices, stiffness matrices, and other
structural analysis matrices.

References:
    [1] Feron J., Latteur P., Almeida J., 2024, Static Modal Analysis, Arch Comp Meth Eng.
    [2] Zhang, Ohsaki, 2015, Tensegrity structures: Form, Stability, and Symmetry
    [3] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm
"""

import numpy as np
from ..femodel.pyelements import PyElements


def compute_equilibrium_matrix(connectivity_matrix, current_coordinates):
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


def compute_global_material_stiffness_matrix(A, flexibility):
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
    # B = A.T  
    
    # Compute the material stiffness matrix
    Km = A @ Ke @ A.T  # (3*n, 3*n)
    return Km



def compute_local_material_stiffness_matrices(cosinus: np.ndarray, flexibility: np.ndarray,) -> list:
        """Compute local material stiffness matrices for each element.
        
        Args:
            cosinus: [-] - shape (elements_count, 3) - Direction cosines of each element
            flexibility: [m/N] - shape (elements_count,) - Element flexibilities L/(EA) based on free_length
            
        Returns:
            List of local material stiffness matrices, each of shape (6,6)
        """
        # Get element count from flexibility array
        elements_count = len(flexibility)
        
        # Assert that cosinus has the correct shape
        assert cosinus.shape == (elements_count, 3), f"cosinus must have shape ({elements_count}, 3), but has shape {cosinus.shape}"
        
        if elements_count == 0:
            return []
        
        km_loc_list = []
        
        for i in range(elements_count):
            cx, cy, cz = cosinus[i]
            cos = np.array([[-cx, -cy, -cz, cx, cy, cz]])
            R = cos.T @ cos  # local compatibility * local equilibrium
            km = (1/flexibility[i]) * R  # local material stiffness matrix
            km_loc_list.append(km)
            
        return km_loc_list


def compute_local_geometric_stiffness_matrices(tension: np.ndarray, length: np.ndarray) -> list:
        """Compute local geometric stiffness matrices for each element.
        
        Args:
            tension: [N] - shape (elements_count,) - Tension in each element
            length: [m] - shape (elements_count,) - Current length of each element
            
        Returns:
            List of local geometric stiffness matrices, each of shape (6,6)
        """
        # Get element count from tension array
        elements_count = len(tension)
        
        # Assert that inputs have the correct shapes
        assert tension.ndim == 1, "tension must be a 1D array"
        assert length.ndim == 1, "length must be a 1D array"
        assert len(length) == elements_count, "length must have the same length as tension"
        
        # Calculate force densities
        force_densities = tension / length
        
        if elements_count == 0:
            return []
            
        kg_loc_list = []
        for i in range(elements_count):
            kg = force_densities[i] * np.array([
                [ 1, 0, 0,-1, 0, 0],
                [ 0, 1, 0, 0,-1, 0],
                [ 0, 0, 1, 0, 0,-1],
                [-1, 0, 0, 1, 0, 0],
                [ 0,-1, 0, 0, 1, 0],
                [ 0, 0,-1, 0, 0, 1]
            ])
            kg_loc_list.append(kg)
            
        return kg_loc_list


def local_to_global_matrix(local_matrices, elements_end_nodes, nodes_count):
    """
    Convert list of local matrices to global matrix.
    
    Args:
        local_matrices: List of local matrices, each of shape (6,6)
        elements_end_nodes: Array of element end nodes, shape (elements_count, 2)
        nodes_count: Number of nodes in the structure
        
    Returns:
        Global  matrix of shape (3*nodes_count, 3*nodes_count)
    """
    # Initialize global  matrix
    K = np.zeros((3*nodes_count, 3*nodes_count))
    
    # Get element count from local_matrices
    elements_count = len(local_matrices)
    
    # Assert that elements_end_nodes has the correct shape
    assert elements_end_nodes.shape == (elements_count, 2), f"elements_end_nodes must have shape ({elements_count}, 2), but has shape {elements_end_nodes.shape}"
    
    if elements_count == 0 or not local_matrices:
        return np.array([], dtype=float)
    
    # Assembly of local matrices into global one
    for i in range(elements_count):
        n0, n1 = elements_end_nodes[i]
        k = local_matrices[i]
        
        # Global indices for the 6 DOFs of the element
        idx = np.array([3*n0, 3*n0+1, 3*n0+2, 3*n1, 3*n1+1, 3*n1+2], dtype=int)
        
        # Add local contributions to global matrix
        for j in range(6):
            for l in range(6):
                K[idx[j], idx[l]] += k[j, l]
                
    return K

