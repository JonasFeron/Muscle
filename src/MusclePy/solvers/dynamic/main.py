from ctypes import ArgumentError
from MusclePy.solvers.dynamic.py_results_dynamic import PyResultsDynamic
from MusclePy.femodel.pytruss import PyTruss
import numpy as np
        

def main_dynamic_modal_analysis(structure: PyTruss, point_masses: np.ndarray = None, 
                               element_masses: np.ndarray = None, element_masses_option: int = 0, 
                               n_modes: int = 0):
    """
    Compute the dynamic modal analysis of a structure.
    
    This function performs modal analysis to determine the natural frequencies and mode shapes
    of a structure with a given mass distribution. It takes into account both the material
    stiffness and geometric stiffness of the structure in its current state.
    
    Args:
        structure: PyTruss
            The structure to analyze. The tangent stiffness matrix will be computed based on 
            the current state of the structure (including any preloading or self-stress).
        point_masses: np.ndarray, optional
            Point masses in kg to be added at each node. Shape should be (nodes_count, 3) 
            for masses in X, Y, Z directions.
        element_masses: np.ndarray, optional
            Element masses in kg. Shape should be (elements_count,). 
        element_masses_option: int, default=0
            Option for handling element masses:
            0: Neglect element masses (only point masses are considered)
            1: Use lumped mass matrix (element mass is split between end nodes)
            2: Use consistent mass matrix (more accurate but not diagonal)
        n_modes: int, default=0
            Number of natural modes to compute. If 0 or greater than available DOFs,
            all possible modes will be computed.
    
    Returns:
        PyResultsDynamic
            Object containing natural frequencies (Hz), mode shapes, and mass matrix
    
    Raises:
        ValueError: If no mass is defined on the structure or masses are negative
        RuntimeError: If eigenvalue computation fails
    """
    # Validate inputs
    assert isinstance(structure, PyTruss), "Input structure must be an instance of PyTruss"
    
    # Get structure information   
    nodes_count = structure.nodes.count
    dof = structure.nodes.dof  # Degrees of Freedom are either True = free, or False = fixed by a support
    n_dof = np.sum(dof)  # Number of free DOFs 

    # Determine how many eigenvalues/eigenvectors to compute 
    # Compute all the modes by default when n_modes=0
    n_modes = n_modes if (n_modes > 0 and n_modes < n_dof) else n_dof
        
    # Compute tangent (material + geometric) stiffness matrix and mass matrix (3*nodes_count, 3*nodes_count)
    K_3n = _compute_tangent_stiffness_matrix(structure)
    M_3n = _compute_mass_matrix(structure, point_masses, element_masses, element_masses_option)

    # Extract stiffness and mass matrices of size (n_dof, n_dof) relative to free DOFs only
    K = K_3n[dof][:, dof]
    M = M_3n[dof][:, dof]
    
    # Solve the generalized eigenvalue problem: K·φ = ω²·M·φ
    try:        
        if n_dof < 100:  # For small problems, use the dense solver 
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

        else:  # For large problems, use the sparse solver which is more efficient
            from scipy.sparse import linalg as sparse_linalg

            # Compute only the smallest eigenvalues (which correspond to the lowest frequencies)
            eigenvalues, eigenvectors = sparse_linalg.eigsh(
                K, 
                k=min(n_modes, n_dof - 1),  # Ensure the number of eigenvalues to compute is valid for the sparse solver
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
        return PyResultsDynamic(frequencies, mode_shapes, M_3n)
        
    except Exception as e:
        raise RuntimeError(f"Eigenvalue computation failed: {e}")


def _compute_tangent_stiffness_matrix(structure: PyTruss):
    """
    Compute the tangent stiffness matrix based on the current state of the structure.
    
    The tangent stiffness matrix is the sum of:
    1. Material stiffness matrix - based on element properties and current geometry
    2. Geometric stiffness matrix - based on current axial forces and geometry
    
    Args:
        structure: PyTruss
            The structure to analyze
            
    Returns:
        np.ndarray
            The global tangent stiffness matrix of shape (3*nodes_count, 3*nodes_count)
    """
    from MusclePy.utils.matrix_calculations import (
        compute_equilibrium_matrix,
        compute_global_material_stiffness_matrix,
        compute_local_geometric_stiffness_matrices,
        local_to_global_matrix
    )
        
    # Compute global material stiffness matrix
    global_material_stiffness_matrix = compute_global_material_stiffness_matrix(
        compute_equilibrium_matrix(structure.elements.connectivity, structure.nodes.coordinates),  # equilibrium matrix based on current nodes coordinates                                    
        structure.elements.flexibility  # current elements flexibility (depends whether the element is in compression or tension)
    )

    # Compute global geometric stiffness matrix
    global_geometric_stiffness_matrix = local_to_global_matrix(
        compute_local_geometric_stiffness_matrices(structure.elements.tension, structure.elements.current_length),
        structure.elements.end_nodes,
        structure.nodes.count
    )
    
    # Sum both matrices to get the tangent stiffness matrix
    global_tangent_stiffness_matrix = global_material_stiffness_matrix + global_geometric_stiffness_matrix
    return global_tangent_stiffness_matrix


def _compute_mass_matrix(structure: PyTruss, point_masses: np.ndarray = None, 
                        element_masses: np.ndarray = None, element_masses_option: int = 0):
    """
    Compute the global mass matrix of the structure.
    
    The mass matrix combines:
    1. Point masses applied at nodes (diagonal matrix)
    2. Element masses (depending on the selected option)
    
    Args:
        structure: PyTruss
            The structure to analyze
        point_masses: np.ndarray, optional
            Point masses in kg at each node. Shape should be (nodes_count, 3)
        element_masses: np.ndarray, optional
            Element masses in kg. Shape should be (elements_count,)
        element_masses_option: int, default=0
            Option for handling element masses:
            0: Neglect element masses
            1: Use lumped mass matrix (diagonal)
            2: Use consistent mass matrix (not diagonal)
            
    Returns:
        np.ndarray
            The global mass matrix of shape (3*nodes_count, 3*nodes_count)
            
    Raises:
        ValueError: If any mass is negative or no mass is defined
        ArgumentError: If an invalid element_masses_option is provided
    """
    from MusclePy.utils.matrix_calculations import (
        compute_local_lumped_mass_matrices,
        compute_local_consistent_mass_matrices,
        local_to_global_matrix
    )
    
    # Get structure dimensions
    nodes_count = structure.nodes.count
    elements_count = structure.elements.count

    # Validate point masses
    point_masses = structure.nodes._check_and_reshape_array(point_masses)
    if np.any(point_masses < 0):
        raise ValueError("All point masses must be positive")
    
    # Validate element masses
    element_masses = structure.elements._check_and_reshape_array(element_masses)
    if np.any(element_masses < 0):
        raise ValueError("All element masses must be positive")
    
    # Initialize element mass matrix
    element_mass_matrix = np.zeros((3*nodes_count, 3*nodes_count))

    # Process element masses based on selected option
    if element_masses_option == 0:
        # Option 0: Neglect element masses
        element_masses = np.zeros(elements_count,)
    
    elif element_masses_option == 1:
        # Option 1: Compute lumped mass matrix (diagonal)
        element_mass_matrix = local_to_global_matrix(
            compute_local_lumped_mass_matrices(element_masses),
            structure.elements.end_nodes,
            nodes_count
        )
    
    elif element_masses_option == 2:
        # Option 2: Compute consistent mass matrix (not diagonal)
        element_mass_matrix = local_to_global_matrix(
            compute_local_consistent_mass_matrices(element_masses),
            structure.elements.end_nodes,
            nodes_count
        )
    
    else:
        raise ArgumentError("Invalid option to compute the element mass matrix. Expected: "
                           "0 to neglect element masses, 1 for lumped mass matrix, or "
                           "2 for consistent mass matrix")

    # Create diagonal matrix with point masses
    point_mass_matrix = np.diag(point_masses.flatten())

    # Combine point masses and element masses
    mass_matrix = point_mass_matrix + element_mass_matrix

    # Verify that the structure has mass
    if np.allclose(mass_matrix, 0, atol=1e-6):
        raise ValueError("No mass defined on the structure")

    return mass_matrix
