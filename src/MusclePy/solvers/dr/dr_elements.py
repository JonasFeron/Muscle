import numpy as np
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.solvers.dr.dr_nodes import DR_Nodes


class DR_Elements(FEM_Elements):
    """
    Extension of FEM_Elements with Dynamic Relaxation specific attributes.
    
    Attributes:
        All attributes from FEM_Elements
        local_geometric_stiffness_matrices: List of local geometric stiffness matrices
    """
    
    def __init__(self, elements_or_nodes, type=None, end_nodes=None, area=None, youngs=None, 
                 free_length_variation=None, tension=None):
        """Initialize a DR_Elements instance.
        
        This constructor accepts either:
        1. A FEM_Elements instance to convert to a DR_Elements instance
        2. A FEM_Nodes (or DR_Nodes) instance plus all parameters (legacy constructor)
        
        Args:
            elements_or_nodes: Either a FEM_Elements instance or a FEM_Nodes (or DR_Nodes) instance
            type: [-] - shape (elements_count,) - Type of elements (-1 for struts, 1 for cables)
            end_nodes: [-] - shape (elements_count, 2) - Indices of end nodes
            area: [mm²] - shape (elements_count,) - Cross-section area of elements
            youngs: [MPa] - shape (elements_count, 2) - Young's moduli for compression and tension
            free_length_variation: [m] - shape (elements_count,) - Change in free length due to prestress
            tension: [N] - shape (elements_count,) - Current tension in elements
        """
        # Check if the first argument is a FEM_Elements instance
        if isinstance(elements_or_nodes, FEM_Elements):
            elements = elements_or_nodes
            
            # Assert that all other arguments are None when a FEM_Elements instance is passed
            assert all(arg is None for arg in [type, end_nodes, area, youngs, free_length_variation, tension]), \
                "When passing a FEM_Elements instance, all other arguments must be None"

            # Call parent class constructor with the properties from the FEM_Elements instance
            super().__init__(
                elements.nodes,
                elements.type,
                elements.end_nodes,
                elements.area,
                elements.youngs,
                elements.free_length_variation,
                elements.tension
            )
        else:
            # Assert that the first argument is a FEM_Nodes or DR_Nodes instance
            assert isinstance(elements_or_nodes, (FEM_Nodes, DR_Nodes)), "First argument must be either a FEM_Elements, FEM_Nodes, or DR_Nodes instance"
            nodes = elements_or_nodes
            # Call parent class constructor with the provided parameters
            super().__init__(nodes, type, end_nodes, area, youngs, free_length_variation, tension)
        
        # Initialize DR-specific attributes
        self._local_geometric_stiffness_matrices = []  # [N/m] - List(elements.count) of shape (6,6) matrices
    
    @property
    def local_geometric_stiffness_matrices(self) -> list:
        """Get the local geometric stiffness matrices."""
        return self._local_geometric_stiffness_matrices
    
    @local_geometric_stiffness_matrices.setter
    def local_geometric_stiffness_matrices(self, value):
        """Set the local geometric stiffness matrices."""
        self._local_geometric_stiffness_matrices = value
    
    def compute_current_state(self):
        """Compute the current state of the elements.
        
        This is a public function to be called once, in order to avoid recomputing 
        the local stiffness matrices at each constructor call.
        """
        self._compute_tension()
        self._compute_stiffness_matrices()
    
    def _compute_tension(self):
        """Compute the tension for each element based on elastic elongation and flexibility."""
        self._tension = self.elastic_elongation / self.flexibility
    
    def _compute_stiffness_matrices(self):
        """Update all local stiffness matrices of the elements based on the current state."""
        from MusclePy.utils.matrix_calculations import compute_local_geometric_stiffness_matrices
        
        # Not used in DR
        # # local material stiffnesses : [N/m] - List(elements.count) of shape (6,6) matrices
        # self.local_material_stiffness_matrices = compute_local_material_stiffness_matrices(
        #     self.direction_cosines,
        #     self.flexibility
        # )
        
        # local geometric stiffnesses : [N/m] - List(elements.count) of shape (6,6) matrices
        self.local_geometric_stiffness_matrices = compute_local_geometric_stiffness_matrices(
            self.tension,
            self.current_length
        )
    
    def _create_copy(self, nodes, type, end_nodes, area, youngs, free_length_variation, tension):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (DR_Elements or a child class)
        """
        return self.__class__(
            nodes,
            type,
            end_nodes,
            area,
            youngs,
            free_length_variation,
            tension
        )
    
    def copy_and_update(self, nodes=None, free_length_variation=None) -> 'DR_Elements':
        """Create a copy of this instance and update its state.
        
        Args:
            nodes: A FEM_Nodes or DR_Nodes instance
            free_length_variation: [m] - shape (elements_count,) - Change in free length due to prestress
            
        Returns:
            A new instance with the updated state
        """
        # Use current values if not provided
        new_nodes = self.nodes if nodes is None else nodes
        free_length_variation = self.free_length_variation if free_length_variation is None else free_length_variation
        
        # Create a new instance with the updated state
        return self._create_copy(
            new_nodes,
            self.type.copy(),
            self.end_nodes.copy(),
            self.area.copy(),
            self.youngs.copy(),
            free_length_variation,
            self.tension.copy()
        )
