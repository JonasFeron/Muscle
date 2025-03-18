from MusclePy.femodel.pyelements import PyElements
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.femodel.prestress_scenario import PrestressScenario


import numpy as np


def main_linear_displacement_method(structure: PyTruss, loads_increment: np.ndarray, 
                                       prestress_increment: PrestressScenario) -> PyTruss:
    """Solve the linear displacement method for a structure with incremental loads and prestress (=free length changes).
    
    This function:
    1. Solves the linear system with combined loads
    2. Updates and returns the structure with the solution
    
    Args:
        structure: Current structure state
        loads_increment: [N] - shape (3*nodes.count,) - External load increments to apply
        prestress_increment: [N] - shape (elements.count,) - Prestress increments to apply
        
    Returns:
        Updated PyTruss with incremented state
    """
    #check input
    assert isinstance(structure, PyTruss), "structure must be an instance of PyTruss"
    assert isinstance(prestress_increment, PrestressScenario), "prestress_increment must be an instance of PrestressScenario"
    loads_increment = structure.nodes._check_and_reshape_array(loads_increment, "loads_increment")
 
    # modify the free length of the elements through mechanical devices
    initial = structure.copy_and_add(free_length_variation=prestress_increment.free_length_variation)

    # Get equivalent prestress loads and tension from free length variations
    eq_prestress = prestress_increment.equivalent_tension
    eq_prestress_loads = prestress_increment.equivalent_loads
    
    # Add prestress loads to external loads
    total_loads_increment = loads_increment + eq_prestress_loads
    
    try:
        # Solve linear system
        displacements, reactions, resisting_forces, tension = core_linear_displacement_method(
            initial, 
            total_loads_increment
        )
        
    except np.linalg.LinAlgError:
        # In case of singular matrix, perturb the structure with tiny displacements
        perturbed = perturb(initial)
        displacements, reactions, resisting_forces, tension = core_linear_displacement_method(
            perturbed, 
            total_loads_increment
        )
    
    # Add the axial prestress force to the resulting axial forces
    tension += eq_prestress
    
    # Update the structure with incremented results
    final_structure = structure.copy_and_add(
        loads_increment=loads_increment,
        displacements_increment=displacements,
        reactions_increment=reactions,
        free_length_variation= prestress_increment.free_length_variation, 
        tension_increment=tension,
        resisting_forces_increment=resisting_forces
    )
    return final_structure


def core_linear_displacement_method(current: PyTruss, loads_increment: np.ndarray):
    """Solve the linear displacement method for the current structure with additional loads.

    Args:
        current: Structure containing the current state
        loads_increment: [N] - shape (3*nodes.count,) - Additional loads to apply
    
    Returns:
        tuple containing:
        - displacements_increment: [m] - shape (3*nodes.count,) - Nodal displacement increments
        - reactions_increment: [N] - shape (fixations.count,) - Support reaction increments
        - tension_increment: [N] - shape (elements.count,) - Element tension increments
    """
    # 0) check input
    assert isinstance(current, PyTruss), "Current must be an instance of PyTruss"
    assert isinstance(loads_increment, np.ndarray), "Loads increment must be a numpy array"
    nodes_count = current.nodes.count
    assert loads_increment.size == 3*nodes_count, f"Loads increment must have size {3*nodes_count} but got {loads_increment.size}"


    # 1) Compute tangent stiffness matrix
    from MusclePy.utils.matrix_calculations import local_to_global_matrix, compute_local_material_stiffness_matrices, compute_local_geometric_stiffness_matrices
        
    # 1.1) local element stiffnesses : [N/m] - List(elements.count) of shape (6,6) matrices
    local_material_stiffness_matrices = compute_local_material_stiffness_matrices(
        current.elements.direction_cosines,
        current.elements.flexibility
    )      
    local_geometric_stiffness_matrices = compute_local_geometric_stiffness_matrices(
        current.elements.tension,
        current.elements.current_length
    )

    # 1.2) Convert local matrices to global matrices of shape (3*nodes.count, 3*nodes.count)
    global_material_stiffness_matrix = local_to_global_matrix(
        local_material_stiffness_matrices,
        current.elements.end_nodes,
        nodes_count
    )
    global_geometric_stiffness_matrix = local_to_global_matrix(
        local_geometric_stiffness_matrices,
        current.elements.end_nodes,
        nodes_count
    )
    # 1.3) tangent stiffness matrix in the current structure state. 
    K = global_material_stiffness_matrix + global_geometric_stiffness_matrix  

    # 1.4) Compute constrained stiffness matrix, accounting for support conditions
    K_constrained = _constrain_stiffness_matrix(current.nodes.dof, K)
    

    # 2) Solve system  K @ d = loads considering also the support conditions (K @ reactions = 0)
    #    see equation 2.7 page 32 of J.Feron's master thesis.

    # 2.1) Build right-hand side vector with loads and imposing zero displacements at support
    rhs = np.zeros((K_constrained.shape[0], 1))
    rhs[:3*nodes_count] = loads_increment.reshape((-1,1))

    # 2.2) Solve system K @ d = loads & K @ reactions = 0
    displacements_reactions = np.linalg.solve(K_constrained, rhs)  

    # 2.3) Extract displacements and reactions
    displacements_increment = displacements_reactions[:3*nodes_count]
    reactions_increment = -displacements_reactions[3*nodes_count:]  


    # 3) Compute tensions by post-processing the displacements
    (tension_increment, resisting_forces_increment) = _post_process(displacements_increment, 
                                                                    local_material_stiffness_matrices, 
                                                                    local_geometric_stiffness_matrices, 
                                                                    current.elements.end_nodes, 
                                                                    current.elements.direction_cosines)

    return (displacements_increment.reshape((-1,)), reactions_increment.reshape((-1,)), resisting_forces_increment.reshape((-1,)), tension_increment.reshape((-1,)))

def perturb(unstable_struct: PyTruss, magnitude: float = 1e-5):
        """Create a copy of the structure with tiny random displacements applied to free DOFs.
        
        This method helps deal with singular stiffness matrices by slightly perturbing the structure.
        The perturbation is only applied to degrees of freedom that are not fixed by supports.
        
        Args:
            magnitude: [m] Standard deviation for the random perturbation. Default is 1e-5 meters.
            
        Returns:
            New DM_Structure with perturbed node coordinates
        """
        # Create random perturbation with specified magnitude
        perturbation = np.random.normal(0, magnitude, size=(unstable_struct.nodes.count, 3))
        
        # Apply perturbation only to free DOFs (True = 1 if free DoF, False = 0 if fixed DoF)
        perturbation = perturbation * unstable_struct.nodes.dof
        
        # Create a copy with the perturbation added to displacements
        perturbed_struct = unstable_struct.copy_and_add(
            displacements_increment=perturbation,  # Add small random displacements
        )        
        return perturbed_struct

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

def _post_process(displacements_increment: np.ndarray,
                 local_material_stiffness_matrices: list, 
                 local_geometric_stiffness_matrices: list,
                 end_nodes: np.ndarray,
                 direction_cosines: np.ndarray) -> np.ndarray:
    """Compute additional element tensions from nodal displacements. Note that tensions are not computed from EA(elastic_elongation)/free_length because,
    in linear calculation, tension must be computed in the initial geometry and not in the deformed geometry (i.e. the compatibility equations have been linearized)
    
    Args:
        displacements_increment: [m] - shape (3*nodes_count,) - Nodal displacements due to additional loads
        
    Returns:
        [N] - shape (elements_count,) - Element tensions
    """
    elements_count = len(local_material_stiffness_matrices)
    assert elements_count == len(local_geometric_stiffness_matrices), "Local stiffness matrices must have the same length"
    
    # Initialize arrays
    tension_increment = np.zeros(elements_count)
    resisting_forces_increment = np.zeros_like(displacements_increment)
    for i in range(elements_count):
        n0, n1 = end_nodes[i]
        index = np.array([3*n0, 3*n0+1, 3*n0+2, 3*n1, 3*n1+1, 3*n1+2])
        d_local = displacements_increment[index]  # Local displacements at element nodes
            
        # Tangent local stiffness matrix
        k_local = local_material_stiffness_matrices[i] + local_geometric_stiffness_matrices[i]
            
        # Local resisting forces at both element ends
        f_local = k_local @ d_local
        resisting_forces_increment[index] += f_local
            
        # Project forces to get tension
        cx, cy, cz = direction_cosines[i]
        tension_increment[i] = -(float(f_local[0])*cx + float(f_local[1])*cy + float(f_local[2])*cz) #axial forces
            
    return (tension_increment, resisting_forces_increment)


