from MusclePy.solvers.dynamic.dynamic_results import DynamicResults
from MusclePy.femodel.pytruss import PyTruss
import numpy as np
        

def main_dynamic_modal_analysis(structure : PyTruss, nodal_masses=None, element_mass_matrices=None, n_modes=0):
    """
    Compute the dynamic modal analysis of a structure.
    
    This function performs modal analysis to determine the natural frequencies and mode shapes
    of a structure with a given mass distribution. It takes into account both the material
    stiffness and geometric stiffness of the structure.
    
    Args:
        structure: PyTruss: The structure to analyze
        nodal_masses: np.ndarray: (nodes_count, 3) Nodal masses in each direction
        element_mass_matrices: list: List of element mass matrices (optional)
        max_frequencies: int: Maximum number of frequencies to compute (0 = all)
    
    Returns:
        DynamicResults: Object containing natural frequencies and mode shapes
    """


    # Validate inputs
    assert isinstance(structure, PyTruss), "Input structure must be an instance of PyTruss"

    nodal_masses = structure.nodes._check_and_reshape_array(nodal_masses)
    if np.any(nodal_masses < 0):
        raise ValueError("All nodal masses must be positive")
    
    # Get structure information   
    nodes_count = structure.nodes.count
    elements_count = structure.elements.count
    dof = structure.nodes.dof # Degrees of Freedom are either True = free, or False = fixed by a support
    n_dof = np.sum(dof) # Number of free DOFs 

    # Determine how many eigenvalues/eigenvectors to compute
    n_modes = n_modes if (n_modes > 0 and n_modes < n_dof) else n_dof
        
    # Compute tangent (material + geometric) stiffness matrix (3*nodes_count, 3*nodes_count)
    K_3n = _compute_tangent_stiffness_matrix(structure)
    
    
    # Fill a diagonal matrix with nodal masses
    nodal_mass_matrix = np.diag(nodal_masses.flatten())

    
    # Add element mass matrices if provided
    if element_mass_matrices is not None and len(element_mass_matrices) == elements_count:
        element_mass_global = local_to_global_matrix(
            element_mass_matrices,
            structure.elements.end_nodes,
            nodes_count
        )
        nodal_mass_matrix += element_mass_global
    
    # Extract free DOF mass matrix
    M = nodal_mass_matrix[dof][:, dof]
    # Extract stiffness matrix of size (n_dof, n_dof) relative to free DOFs only
    K = K_3n[dof][:, dof]
    
    # Solve the generalized eigenvalue problem: K·φ = ω²·M·φ
    try:        

                
        if n_dof < 100: # For small problems, use the dense solver which is more accurate
            from scipy import linalg
            eigenvalues, eigenvectors = linalg.eigh(K, M)
            
            # Sort frequencies and eigenvectors
            sort_indices = np.argsort(eigenvalues)
            eigenvalues = eigenvalues[sort_indices]
            eigenvectors = eigenvectors[:, sort_indices]
            
            # Limit the number of frequencies if requested (only needed for dense solver)
            if n_modes < n_dof:
                eigenvalues = eigenvalues[:n_modes]
                eigenvectors = eigenvectors[:, :n_modes]


        else: # for large problems, use the sparse solver which is more efficient
            from scipy.sparse import linalg as sparse_linalg

            # Compute only the smallest eigenvalues (which correspond to the lowest frequencies)
            eigenvalues, eigenvectors = sparse_linalg.eigsh(
                K, 
                k=min(n_modes, n_dof - 1), # Ensure the number of eigenvalue to compute is valid for the sparse solver
                M=M,
                sigma=0.0,  # Target eigenvalues near zero
                which='SM'   # Get smallest magnitude eigenvalues
            )
            
        # Convert eigenvalues (=ω²) to frequencies
        angular_frequencies = np.sqrt(np.abs(eigenvalues))  
        frequencies = angular_frequencies / (2 * np.pi)  # Convert to Hz
        
        # Create mode shapes (including fixed DOFs)
        mode_shapes = np.zeros((3 * nodes_count, eigenvectors.shape[1]))
        mode_shapes[dof] = eigenvectors
        
        # Create and return results object
        return DynamicResults(frequencies,mode_shapes)
        
    except Exception as e:
        raise RuntimeError(f"Eigenvalue computation failed: {e}")

def _compute_tangent_stiffness_matrix(structure: PyTruss):
    """Compute the tangent stiffness matrix based on the current state."""
    from MusclePy.utils.matrix_calculations import (
        compute_equilibrium_matrix,
        compute_global_material_stiffness_matrix,
        compute_local_geometric_stiffness_matrices,
        local_to_global_matrix
    )
        
    # Compute global material stiffness matrix
    global_material_stiffness_matrix = compute_global_material_stiffness_matrix(
        compute_equilibrium_matrix(structure.elements.connectivity,structure.nodes.coordinates), #equilibrium matrix based on current nodes coordinates                                    
        structure.elements.flexibility # current elements flexibility (depends whether the element is in compression or tension)
    )

    # Compute global geometric stiffness matrix
    global_geometric_stiffness_matrix = local_to_global_matrix(
        compute_local_geometric_stiffness_matrices(structure.elements.tension, structure.elements.current_length),
        structure.elements.end_nodes,
        structure.nodes.count
    )
    
    global_tangent_stiffness_matrix = global_material_stiffness_matrix + global_geometric_stiffness_matrix
    return global_tangent_stiffness_matrix


