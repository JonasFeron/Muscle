from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.solvers.linear_dm.structure_linear_dm import Structure_Linear_DM
import numpy as np

def equivalent_prestress_loads(elements:FEM_Elements, delta_free_length_increment:np.ndarray):
        """Transform free length variations (imposed by mechanical devices) into equivalent prestress loads.
        
        This function computes:
        1. The axial force in each element that would result from the free length variations assuming all nodes are fixed.
        2. The equivalent external loads, to apply on the structure through linear displacement method, 
           that would produce the same effect as the free length variations. 
        
        Args:
            elements: FEM_Elements instance containing element properties and current state
            delta_free_length_increment: [m] - shape (elements.count,) - free length variations (imposed by mechanical devices)
            
        Returns:
            tuple containing:
            - eq_prestress: [N] - shape (elements.count,) - Axial force in each element
            - eq_prestress_loads: [N] - shape (3*nodes.count,) - Equivalent external loads
        """
        d_l0 = delta_free_length_increment 
        Ke = 1/elements.flexibility
        nodes_count = elements.nodes.count

        # 1) Compute the tension
        t = Ke * - d_l0  # [N] - shape (elements_count,) -  t = EA/Lfree * (-d_l0). A lengthening d_l0 (+) creates a compression force (-), supposing all nodes are fixed.
        eq_prestress = t

        #2) Compute the equivalent prestress loads
        eq_prestress_loads = np.zeros((nodes_count, 3))  # Shape (nodes_count, 3)
        direction_cosines = elements.direction_cosines
        end_nodes = elements.end_nodes
        
        for i in range(elements.count):
            cx, cy, cz = direction_cosines[i]
            n0, n1 = end_nodes[i]  # Get start and end nodes
            
            # Apply forces to start node (negative)
            eq_prestress_loads[n0] += -t[i] * np.array([-cx, -cy, -cz])
            
            # Apply forces to end node (positive)
            eq_prestress_loads[n1] += -t[i] * np.array([cx, cy, cz])
            
        return (eq_prestress, eq_prestress_loads)


def perturb_structure(structure: Structure_Linear_DM, magnitude: float = 1e-5) -> Structure_Linear_DM:
    """Create a copy of the structure with tiny random displacements applied to free DOFs.
    
    This function helps deal with singular stiffness matrices by slightly perturbing the structure.
    The perturbation is only applied to degrees of freedom that are not fixed by supports.
    
    Args:
        structure: Structure to perturb
        magnitude: Standard deviation for the random perturbation. Default is 1e-5 meters.
        
    Returns:
        New Structure_Linear_DM with perturbed displacements
    """
    # Create random perturbations for all DOFs
    nodes_count = structure.nodes.count
    perturbation = np.random.normal(0, magnitude, size=(3 * nodes_count,))
    
    # Zero out perturbations where DOFs are fixed
    perturbation[~structure.nodes.dof] = 0
    
    # Create perturbed structure by adding tiny displacements
    perturbed = structure.copy_and_add(
        loads_increment=np.zeros_like(perturbation),  # No additional loads
        displacements_increment=perturbation,
        reactions_increment=np.zeros_like(perturbation),  # No additional reactions
        delta_free_length_increment=np.zeros(structure.elements.count),  # No change in free length
        tension_increment=np.zeros(structure.elements.count)  # No change in tension
    )
    
    return perturbed
