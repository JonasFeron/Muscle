from .fem_nodes import FEM_Nodes
from .fem_elements import FEM_Elements
import numpy as np

class FEM_Structure:
    def __init__(self, nodes: FEM_Nodes, elements: FEM_Elements):
        """Python equivalent of C# FEM_Structure class, combining nodes and elements.
        
        This class serves as a container for both nodes and elements, ensuring they remain
        consistent with each other.
        
        Args:
            nodes: FEM_Nodes instance containing nodal data
            elements: FEM_Elements instance that must reference the same nodes instance
        """
        if not isinstance(nodes, FEM_Nodes):
            raise TypeError("nodes must be a FEM_Nodes instance")
        if not isinstance(elements, FEM_Elements):
            raise TypeError("elements must be a FEM_Elements instance")
        if elements.nodes is not nodes:
            raise ValueError("elements must reference the same nodes instance")
        
        self._nodes = nodes
        self._elements = elements
    
    @property
    def nodes(self) -> FEM_Nodes:
        """Get the FEM_Nodes instance."""
        return self._nodes
    
    @property
    def elements(self) -> FEM_Elements:
        """Get the FEM_Elements instance."""
        return self._elements

    def is_in_equilibrium(self, rtol: float = 1e-4, atol: float = 1e-6) -> bool:
        """Check if the structure is in equilibrium, i.e. all residuals are zero for each DOF.
        
        Args:
            rtol: Relative tolerance for zero residual check, compared to external loads.
            atol: Absolute tolerance for zero residual check, when load is near zero for a certain DOF.
            
        Returns:
            True if the structure is in equilibrium, False otherwise
        """
        # Calculate (residuals == 0) threshold based on load 
        zero_residuals_threshold = rtol * np.abs(self.nodes.loads) + atol # [N] shape (nodes_count, 3)
        
        return np.all(np.abs(self.nodes.residuals) <= zero_residuals_threshold)

    
    def _create_copy(self, nodes, elements):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (FEM_Structure or a child class)
        """
        return self.__class__(nodes, elements)
        
    def copy(self) -> 'FEM_Structure':
        """Create a copy of this structure with the current state.
        
        Returns:
            A new instance with the current state
        """
        # Create new nodes with current state
        nodes_copy = self._nodes.copy()
        
        # Create new elements with current state, referencing the new nodes
        elements_copy = self._elements.copy(nodes_copy)
        
        return self._create_copy(nodes_copy, elements_copy)
    
    def copy_and_update(self, loads: np.ndarray = None, displacements: np.ndarray = None, reactions: np.ndarray = None,
                       free_length: np.ndarray = None, tension: np.ndarray = None, resisting_forces: np.ndarray = None):
        """Create a copy of this structure and update its state, or use the current state if None is passed.
        
        Args:
            loads: [N] - shape (nodes_count, 3) or (3*nodes_count,) - External loads
            displacements: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Support reactions
            free_length: [m] - shape (elements_count,) - Free length of elements
            tension: [N] - shape (elements_count,) - Axial forces
            resisting_forces: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Internal resisting forces
        """
        # Create new nodes with updated state
        nodes_copy = self._nodes.copy_and_update(loads, displacements, reactions, resisting_forces)
        
        # Create new elements with updated state, referencing the new nodes
        elements_copy = self._elements.copy_and_update(nodes_copy, free_length, tension)
        
        return self._create_copy(nodes_copy, elements_copy)
        
    def copy_and_add(self, loads_increment: np.ndarray = None, displacements_increment: np.ndarray = None, 
                     reactions_increment: np.ndarray = None, free_length_variation: np.ndarray = None,
                     tension_increment: np.ndarray = None, resisting_forces_increment: np.ndarray = None) -> 'FEM_Structure':
        """Create a copy of this structure and add increments to its state.
        
        Args:
            loads_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Load increments
            displacements_increment: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Displacement increments
            reactions_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Reaction increments
            free_length_variation: [m] - shape (elements_count,) - Increment in free length
            tension_increment: [N] - shape (elements_count,) - Increment in axial forces
            resisting_forces_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Increment in resisting forces
        """
        # Create new nodes with incremented state
        nodes_copy = self._nodes.copy_and_add(loads_increment, displacements_increment, reactions_increment, resisting_forces_increment)
        
        # Create new elements with incremented state, referencing the new nodes
        elements_copy = self._elements.copy_and_add(nodes_copy, free_length_variation, tension_increment)
        
        return self._create_copy(nodes_copy, elements_copy)
