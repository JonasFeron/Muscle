from MusclePy.solvers.linear_dm.structure_state_4linear_dm import Structure_State_4Linear_DM
import numpy as np

def linear_displacement_method(current: Structure_State_4Linear_DM, additional_loads: np.ndarray):
    """Solve the linear displacement method for the current structure with additional loads.
    
    Args:
        current: Structure_State_4Linear_DM instance containing the current state
        additional_loads: [N] - shape (3*nodes.count,) - Additional loads to apply
        
    Returns:
        tuple containing:
        - displacements: [m] - shape (3*nodes.count,) - Nodal displacements
        - tension: [N] - shape (elements.count,) - Element tensions
        - reactions: [N] - shape (fixations.count,) - Support reactions
    """
    # Get structure properties
    nodes_count = current.nodes.count
    fixations_count = current.nodes.fixations_count

    # Reshape loads to column vector
    loads = additional_loads.reshape((-1, 1))
    
    # Get stiffness matrices
    Km = current.global_material_stiffness_matrix
    Kg = current.global_geometric_stiffness_matrix
    K = Km + Kg  # tangent stiffness matrix in the current structure state. 
    
    # Apply support conditions
    K_constrained = _constrain_stiffness_matrix(dof=current.nodes.dof,
                                              stiffness_matrix=K)
    
    # Build right-hand side vector with loads and zero reactions
    rhs = np.zeros((K_constrained.shape[0], 1))
    rhs[:3*nodes_count] = loads
    
    # Solve system loads = K @ d considering also the support conditions
    displacements_reactions = np.linalg.solve(K_constrained, rhs)  # see equation 2.7 page 32 of J.Feron's master thesis.
    
    # Extract displacements and reactions
    displacements = displacements_reactions[:3*nodes_count]
    reactions = -displacements_reactions[3*nodes_count:]
    
    # Compute tensions using post-processing
    tension = current.elements.post_process(displacements)

    return (displacements.reshape((-1,)), tension.reshape((-1,)), reactions.reshape((-1,)))


def _constrain_stiffness_matrix(dof: np.ndarray, stiffness_matrix: np.ndarray) -> np.ndarray:
    """Apply support conditions to the stiffness matrix of the structure.
    
    Args:
        dof: [-] - shape (nodes_count, 3) - Degrees of freedom of nodes (True if free, False if fixed)
        stiffness_matrix: [N/m] - shape (3*nodes_count, 3*nodes_count) - Global stiffness matrix
            
    Returns:
        [N/m] - shape (3*nodes_count + fixations_count, 3*nodes_count + fixations_count) - Constrained stiffness matrix
    """
    # Get dimensions from input arrays
    n = stiffness_matrix.shape[0] // 3  # nodes_count
    assert stiffness_matrix.shape == (3*n, 3*n), "Stiffness matrix must have shape (3*nodes_count, 3*nodes_count)"
    assert n > 0, "Structure must have at least one node"
    assert dof.shape == (n, 3), f"DOF array must have shape ({n}, 3) but got {dof.shape}"
    
    # Get number of fixed DOFs
    dof_flat = dof.reshape(-1)  # Flatten to 1D array
    c = np.sum(~dof_flat)  # fixations_count
    assert c > 0, "Structure must have at least one fixed DOF"
    
    # Get indices of fixed DOFs
    fixed_dof_indices = np.arange(3*n)[~dof_flat]
    
    # Create constraint matrix
    constraints = np.zeros((c, 3*n))
    for i, dof_index in enumerate(fixed_dof_indices):
        constraints[i, dof_index] = 1
    
    # Build constrained stiffness matrix
    K_constrained = np.zeros((3*n + c, 3*n + c))
    K_constrained[:3*n, :3*n] = stiffness_matrix
    K_constrained[3*n:, :3*n] = constraints
    K_constrained[:3*n, 3*n:] = constraints.T
    
    return K_constrained
