from .solvers.linear_dm.structure_linear_dm import Structure_Linear_DM
from .solvers.linear_dm.elements_linear_dm import Elements_Linear_DM
from .solvers.linear_dm.linear_dm import linear_displacement_method
from .solvers.linear_dm.helper_main_linear_dm import equivalent_prestress_loads, perturb_structure
from .femodel.fem_structure import FEM_Structure
from .femodel.fem_nodes import FEM_Nodes
import numpy as np


def main_linear_displacement_method(structure: FEM_Structure, loads_increment: np.ndarray, 
                                  free_length_increment: np.ndarray) -> FEM_Structure:
    """Solve the linear displacement method for a structure with incremental loads and prestress (=free length changes).
    
    This function:
    1. Converts the structure to a linear DM compatible structure
    2. Computes equivalent prestress loads from free length changes
    3. Solves the linear system with combined loads
    4. Updates and returns the structure with the solution
    
    Args:
        structure: Current structure state
        loads_increment: [N] - shape (3*nodes.count,) - External load increments to apply
        free_length_increment: [m] - shape (elements.count,) - Free length increments to apply
        
    Returns:
        Updated FEM_Structure with incremented state
    """
    #check input shapes
    loads_increment = structure.nodes._check_and_reshape_array(loads_increment, "loads_increment")
    free_length_increment = structure.elements._check_and_reshape_array(free_length_increment, "delta_free_length_increment")
 
    # modify the free length of the elements via mechanical devices
    total_free_length_variation = structure.elements.delta_free_length + free_length_increment

    # Create a linear structure for the Displacement Method 
    # Elements_Linear_DM is a child class of FEM_Elements with extended element properties (local stiffness matrices)
    linear_elements = Elements_Linear_DM(
        nodes=structure.nodes,
        type=structure.elements.type,
        end_nodes=structure.elements.end_nodes,
        areas=structure.elements.areas,
        youngs=structure.elements.youngs,
        delta_free_length=total_free_length_variation,
        tension=structure.elements.tension
    )
    
    # Structure_Linear_DM is a child class of FEM_Structure with extended properties (global stiffness matrices)
    linear = Structure_Linear_DM(structure.nodes, linear_elements)
    
    # Compute equivalent prestress loads from free length variations
    eq_prestress, eq_prestress_loads = equivalent_prestress_loads(
        linear.elements, 
        free_length_increment
    )
    
    # Add prestress loads to external loads
    total_loads_increment = loads_increment + eq_prestress_loads
    
    try:
        # Solve linear system
        displacements, reactions, resisting_forces, tension = linear_displacement_method(
            linear, 
            total_loads_increment
        )
        
    except np.linalg.LinAlgError:
        # In case of singular matrix, perturb the structure with tiny displacements
        perturbed = perturb_structure(linear)
        displacements, reactions, resisting_forces, tension = linear_displacement_method(
            perturbed, 
            total_loads_increment
        )
    
    # Add the axial prestress force (equivalent to the free length variations) to the resulting axial forces 
    tension += eq_prestress
    
    # Create updated structure with incremented state using parent class method
    return structure.copy_and_add(
        loads_increment=loads_increment,
        displacements_increment=displacements,
        reactions_increment=reactions,
        delta_free_length_increment=free_length_increment, #No, the free_length_increment is not added twice to the structure
        tension_increment=tension,
        resisting_forces_increment=resisting_forces
    )