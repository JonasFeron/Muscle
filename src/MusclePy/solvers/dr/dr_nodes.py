import numpy as np
from MusclePy.femodel.fem_nodes import FEM_Nodes


class DR_Nodes(FEM_Nodes):
    """
    Extension of FEM_Nodes with Dynamic Relaxation specific attributes.
    
    Attributes:
        All attributes from FEM_Nodes
        velocities: [m/s] - shape (nodes_count, 3) - Nodal velocities
        resisting_forces: [N] - shape (nodes_count, 3) - Resisting forces
    """
    
    def __init__(self, nodes_or_inititialcoordinates, dof=None, loads=None, displacements=None, 
                 reactions=None, resisting_forces=None, velocities=None):
        """Initialize a DR_Nodes instance.
        
        Args:
            nodes_or_coordinates: Either a FEM_Nodes instance or a numpy array of shape (nodes_count, 3) containing nodal coordinates
            dof: [bool] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)
            loads: [N] - shape (nodes_count, 3) - External loads
            displacements: [m] - shape (nodes_count, 3) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) - Support reactions
            resisting_forces: [N] - shape (nodes_count, 3) - Resisting forces
            velocities: [m/s] - shape (nodes_count, 3) - Nodal velocities
        """
        # Check if the first argument is a FEM_Nodes instance
        if isinstance(nodes_or_inititialcoordinates, FEM_Nodes):
            nodes = nodes_or_inititialcoordinates
            # Call parent class constructor with the FEM_Nodes instance
            super().__init__(
                nodes.initial_coordinates,
                nodes.dof,
                nodes.loads,
                nodes.displacements,
                nodes.reactions,
                nodes.resisting_forces
            )
        else:
            # Call parent class constructor with the provided parameters
            initial_coordinates = nodes_or_inititialcoordinates
            super().__init__(initial_coordinates, dof, loads, displacements, reactions, resisting_forces)
        
        # Initialize DR-specific attributes
        self._velocities = self._check_and_reshape_array(velocities, "velocities")

        self._computed_reactions = False
        self._computed_resisting_forces = False
    
    @property
    def velocities(self) -> np.ndarray:
        """[m/s] - shape (nodes_count, 3) - Nodal velocities"""
        return self._velocities
    
    # redundant with parent class
    # @property
    # def reactions(self) -> np.ndarray:
    #     """[N] - shape (nodes_count, 3) - Support reactions"""
    #     return self._reactions

    # @property
    # def resisting_forces(self) -> np.ndarray:
    #     """[N] - shape (nodes_count, 3) - Resisting forces"""
    #     return self._resisting_forces
    
    @resisting_forces.setter
    def resisting_forces(self, value):
        """Set resisting forces. Resisting forces are set by DR_Structure instance once the equilibrium matrix is computed."""
        self._computed_resisting_forces = True
        self._resisting_forces = self._check_and_reshape_array(value, "resisting_forces")
    
    def compute_reactions(self):
        """Compute support reactions and store them in the _reactions attribute."""
        assert self._computed_resisting_forces, "Impossible to compute reactions, without computing resisting forces first."
        reactions = np.zeros_like(self.resisting_forces)
        where_supports = ~self.dof.astype(bool)
        reactions[where_supports] = self.loads[where_supports] - self.resisting_forces[where_supports]
        self._reactions = reactions
        self._computed_reactions = True

    @property
    def residuals(self) -> np.ndarray:
        """[N] - shape (nodes_count, 3) - Residual forces (loads - resisting_forces - reactions)"""
        assert self._computed_resisting_forces, "Impossible to compute residuals, without computing resisting forces first."
        assert self._computed_reactions, "Impossible to compute residuals, without computing reactions first."

        # Compute residuals
        return self._loads + self._reactions - self._resisting_forces
    
    
    def _create_copy(self, initial_coordinates, dof, loads, displacements, reactions, resisting_forces, velocities=None):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (DR_Nodes or a child class)
        """
        v = self._velocities if velocities is None else velocities
        return self.__class__(
            initial_coordinates,
            dof,
            loads,
            displacements,
            reactions,
            resisting_forces,
            v,
        )
    
    def copy(self) -> 'DR_Nodes':
        """Create a copy of this instance with the current state.
        
        Returns:
            A new instance with the current state
        """
        return self._create_copy(
            self._initial_coordinates.copy(),
            self._dof.copy(),
            self._loads.copy(),
            self._displacements.copy(),
            self._reactions.copy(),
            self._resisting_forces.copy(),
            self._velocities.copy(),
        )
    
    def copy_and_update(self, loads=None, displacements=None, velocities=None) -> 'DR_Nodes':
        """Create a copy of this instance and update its state.
        
        Args:
            loads: [N] - shape (nodes_count, 3) - External loads
            displacements: [m] - shape (nodes_count, 3) - Nodal displacements
            velocity: [m/s] - shape (nodes_count, 3) - Nodal velocities
            masses: [kg] - shape (nodes_count, 3) - Nodal masses
            
        Returns:
            A new instance with the updated state
        """
        # Handle None values by using current state
        if loads is None: loads = self._loads.copy()
        if displacements is None: displacements = self._displacements.copy()
        if velocities is None: velocities = self._velocities.copy()
        
        # Reshape inputs if needed
        loads = self._check_and_reshape_array(loads, "loads")
        displacements = self._check_and_reshape_array(displacements, "displacements")
        velocities = self._check_and_reshape_array(velocities, "velocities")
        
        # Create a new instance with the updated state
        return self._create_copy(
            self._initial_coordinates.copy(),
            self._dof.copy(),
            loads,
            displacements,
            self._reactions.copy(),
            self._resisting_forces.copy(),
            velocities
        )
