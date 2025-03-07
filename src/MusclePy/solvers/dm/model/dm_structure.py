from MusclePy.solvers.dm.model.dm_elements import DM_Elements
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
import numpy as np


class DM_Structure(FEM_Structure):
    def __init__(self, nodes_or_structure, elements=None):
        """Initialize DM_Structure, extending FEM_Structure with stiffness matrices.
        
        This constructor accepts either:
        1. A FEM_Structure instance to convert to a DM_Structure instance
        2. A FEM_Nodes instance and a FEM_Elements or DM_Elements instance
        
        Args:
            nodes_or_structure: Either a FEM_Structure instance or a FEM_Nodes instance
            elements: Either a FEM_Elements or DM_Elements instance, only used if nodes_or_structure is FEM_Nodes
        """
        # Check if the first argument is a FEM_Structure instance
        if isinstance(nodes_or_structure, FEM_Structure) and elements is None:
            structure = nodes_or_structure
            nodes = structure.nodes
            
            # Convert elements to DM_Elements if needed
            if not isinstance(structure.elements, DM_Elements):
                elements = DM_Elements(structure.elements)
            else:
                elements = structure.elements
                
            # Call parent class constructor
            super().__init__(nodes, elements)
        else:
            # Assert that the first argument is a FEM_Nodes instance
            assert isinstance(nodes_or_structure, FEM_Nodes), "First argument must be either a FEM_Structure or a FEM_Nodes instance"
            
            # First argument is a FEM_Nodes instance
            nodes = nodes_or_structure
            
            # Assert that elements is not None when nodes_or_structure is not a FEM_Structure
            assert elements is not None, "When passing a FEM_Nodes instance, elements must not be None"
            
            # Convert elements to DM_Elements if needed
            if elements is not None and not isinstance(elements, DM_Elements):
                elements = DM_Elements(elements)
                
            # Call parent class constructor
            super().__init__(nodes, elements)
        
        # Initialize stiffness matrices attributes
        self.global_material_stiffness_matrix = None  # [N/m] - shape (3*nodes.count, 3*nodes.count)
        self.global_geometric_stiffness_matrix = None  # [N/m] - shape (3*nodes.count, 3*nodes.count)

        self._compute_stiffness_matrices()

    def _compute_stiffness_matrices(self):
        """Compute all global stiffness matrices for the structure.
        
        This method computes:
        1. Global material stiffness matrix
        2. Global geometric stiffness matrix
        """
        from MusclePy.utils.matrix_calculations import local_to_global_stiffness_matrix

        # Convert local matrices to global matrices using utility function
        self.global_material_stiffness_matrix = local_to_global_stiffness_matrix(
            self.elements.local_material_stiffness_matrices,
            self.elements.end_nodes,
            self.nodes.count
        )
        self.global_geometric_stiffness_matrix = local_to_global_stiffness_matrix(
            self.elements.local_geometric_stiffness_matrices,
            self.elements.end_nodes,
            self.nodes.count
        )

    def perturb(self, magnitude: float = 1e-5):
        """Create a copy of the structure with tiny random displacements applied to free DOFs.
        
        This method helps deal with singular stiffness matrices by slightly perturbing the structure.
        The perturbation is only applied to degrees of freedom that are not fixed by supports.
        
        Args:
            magnitude: [m] Standard deviation for the random perturbation. Default is 1e-5 meters.
            
        Returns:
            New DM_Structure with perturbed node coordinates
        """
        # Create random perturbation with specified magnitude
        perturbation = np.random.normal(0, magnitude, size=(self.nodes.count, 3))
        
        # Apply perturbation only to free DOFs
        perturbation = perturbation * self.nodes.dof
        
        # Create a copy with the perturbation added to displacements
        perturbed = self.copy_and_add(
            displacements_increment=perturbation,  # Add small random displacements
            loads_increment=np.zeros_like(perturbation),  # No additional loads
            reactions_increment=np.zeros_like(perturbation),  # No additional reactions
            delta_free_length_increment=np.zeros(self.elements.count),  # No change in free length
            tension_increment=np.zeros(self.elements.count),  # No change in tension
            resisting_forces_increment=np.zeros_like(perturbation)  # No change in resisting forces
        )
        
        return perturbed
    
    def _create_copy(self, nodes, elements):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (DM_Structure or a child class)
        """
        return self.__class__(nodes, elements)
