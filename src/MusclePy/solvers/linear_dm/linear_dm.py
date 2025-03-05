from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.solvers.linear_dm.structure_linear_dm import Structure_Linear_DM
from MusclePy.solvers.linear_dm.elements_linear_dm import Elements_Linear_DM
import numpy as np


class LinearDisplacementMethod:
    """Static class containing methods for linear displacement method analysis."""

    @staticmethod
    def apply_loads_and_prestress_increments(structure: FEM_Structure, loads_increment: np.ndarray, 
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

        initial_state = Structure_Linear_DM(
            nodes=structure.nodes,
            elements=Elements_Linear_DM(
                nodes=structure.nodes,
                type=structure.elements.type,
                end_nodes=structure.elements.end_nodes,
                areas=structure.elements.areas,
                youngs=structure.elements.youngs,
                delta_free_length=total_free_length_variation,   # modify the free length of the elements via mechanical devices
                tension=structure.elements.tension
            )
        )
        
        # Compute equivalent prestress loads from free length variations
        eq_prestress, eq_prestress_loads = LinearDisplacementMethod._equivalent_prestress_loads(
            initial_state.elements, 
            free_length_increment
        )
        
        # Add prestress loads to external loads
        total_loads_increment = loads_increment + eq_prestress_loads
        
        try:
            # Solve linear system
            displacements, reactions, resisting_forces, tension = LinearDisplacementMethod._core(
                initial_state, 
                total_loads_increment
            )
            
        except np.linalg.LinAlgError:
            # In case of singular matrix, perturb the structure with tiny displacements
            perturbed = LinearDisplacementMethod._perturb_structure(initial_state)
            displacements, reactions, resisting_forces, tension = LinearDisplacementMethod._core(
                perturbed, 
                total_loads_increment
            )
        
        # Add the axial prestress force (equivalent to the free length variations) to the resulting axial forces 
        tension += eq_prestress
        
        # Update the inputted structure with incremented results
        deformed_state = structure.copy_and_add(
            loads_increment=loads_increment,
            displacements_increment=displacements,
            reactions_increment=reactions,
            delta_free_length_increment=free_length_increment, #No, the free_length_increment is not added twice to the structure
            tension_increment=tension,
            resisting_forces_increment=resisting_forces
        )
        return deformed_state

    @staticmethod
    def _core(current: Structure_Linear_DM, loads_increment: np.ndarray):
        """Solve the linear displacement method for the current structure with additional loads.
    
        Args:
            current: Structure_Linear_DM instance containing the current state
            loads_increment: [N] - shape (3*nodes.count,) - Additional loads to apply
        
        Returns:
            tuple containing:
            - displacements_increment: [m] - shape (3*nodes.count,) - Nodal displacement increments
            - reactions_increment: [N] - shape (fixations.count,) - Support reaction increments
            - tension_increment: [N] - shape (elements.count,) - Element tension increments
        """
        # Get structure properties
        nodes_count = current.nodes.count

        # Compute global stiffness matrix
        Km = current.global_material_stiffness_matrix
        Kg = current.global_geometric_stiffness_matrix
        K = Km + Kg  # tangent stiffness matrix in the current structure state. 

        # Compute constrained stiffness matrix
        K_constrained = LinearDisplacementMethod._constrain_stiffness_matrix(current.nodes.dof, K)
        
        # Build right-hand side vector with loads and zero reactions
        rhs = np.zeros((K_constrained.shape[0], 1))
        rhs[:3*nodes_count] = loads_increment.reshape((-1,1))
    
        # Solve system loads = K @ d considering also the support conditions
        displacements_reactions = np.linalg.solve(K_constrained, rhs)  # see equation 2.7 page 32 of J.Feron's master thesis.
    
        # Extract displacements and reactions
        displacements_increment = displacements_reactions[:3*nodes_count]
        reactions_increment = -displacements_reactions[3*nodes_count:]  
    
        # Compute tensions using post-processing
        (tension_increment, resisting_forces_increment) = current.elements.post_process(displacements_increment)

        return (displacements_increment.reshape((-1,)), reactions_increment.reshape((-1,)), resisting_forces_increment.reshape((-1,)), tension_increment.reshape((-1,)))

    @staticmethod
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

    @staticmethod
    def _equivalent_prestress_loads(elements: FEM_Elements, delta_free_length_increment: np.ndarray):
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

    @staticmethod
    def _perturb_structure(structure: Structure_Linear_DM, magnitude: float = 1e-5) -> Structure_Linear_DM:
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
