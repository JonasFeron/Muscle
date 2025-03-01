import numpy as np
from typing import Optional

class FEM_Nodes:
    def __init__(self, initial_coordinates=None, dof=None, loads=None, displacements=None, reactions=None, resisting_forces=None):
        """Python equivalent of C# FEM_Nodes class, combining nodes state and results.
        
        The class has two types of attributes:
        1. Immutable attributes (initialized once from C#):
            - initial_coordinates: Initial nodal coordinates
            - dof: Degrees of freedom (support conditions)
            - count: Number of nodes
            - fixations_count: Number of fixed DOFs
            
        2. Mutable state attributes:
            - loads: external loads applied to nodes
            - displacements: Nodal displacements
            - reactions: Support reactions
            - resisting_forces: Internal resisting forces at nodes
            - coordinates: Current nodal coordinates (initial_coordinates + displacements)
            - residual: Out of balance forces
        
        Args:
            initial_coordinates: [m] - shape (nodes_count, 3) - Initial nodal coordinates
            dof: [-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)
            loads: [N] - shape (nodes_count, 3) - External loads applied to nodes
            displacements: [m] - shape (nodes_count, 3) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) - Support reactions
            resisting_forces: [N] - shape (nodes_count, 3) - Internal resisting forces at nodes
        """
        # Initialize immutable attributes (set once from C#)
        self._initial_coordinates = np.array([], dtype=float).reshape((0, 3))
        self._dof = np.array([], dtype=bool).reshape((0, 3))
        self._count = 0
        self._fixations_count = 0
        
        # Initialize mutable state attributes
        self._loads = np.array([], dtype=float).reshape((0, 3))
        self._displacements = np.array([], dtype=float).reshape((0, 3))
        self._reactions = np.array([], dtype=float).reshape((0, 3))
        self._resisting_forces = np.array([], dtype=float).reshape((0, 3))
        self._residual = np.array([], dtype=float).reshape((0, 3))
        
        # Initialize the instance
        self._initialize(initial_coordinates, dof, loads, displacements, reactions, resisting_forces)
    
    def _check_array(self, arr, name):
        """Check and convert array to proper numpy array with correct shape."""
        if arr is not None:
            result = arr if isinstance(arr, np.ndarray) else np.array(arr, dtype=float)
            assert result.shape == (self._count, 3), f"{name} should have shape ({self._count}, 3) but got {result.shape}"
            return result
        return np.zeros((self._count, 3), dtype=float)
    
    def _reshape_array(self, arr, name) -> np.ndarray:
        """Reshape array to proper shape (nodes_count, 3) if possible.
        
        Handles these cases:
        1. None -> zeros array
        2. Shape (nodes_count, 3) -> unchanged
        3. Shape (3*nodes_count,) -> reshaped to (nodes_count, 3)
        4. Shape (fixations_count,) -> expanded to (3*nodes_count,) and reshaped
        
        Args:
            arr: Array to reshape
            name: Name of array for error messages
            
        Returns:
            Reshaped array of shape (nodes_count, 3)
        """
        if arr is None:
            return np.zeros((self._count, 3), dtype=float)
        
        # Convert to numpy array if needed
        result = arr if isinstance(arr, np.ndarray) else np.array(arr, dtype=float)
        
        # If already correct shape, return as is
        if result.shape == (self._count, 3):
            return result
        
        # Try to reshape if it's a flat array
        if result.size == self._count * 3:
            try:
                return result.reshape(self._count, 3)
            except ValueError:
                pass  # Fall through to next case
                
        # Handle reactions array from fixations_count to nodes_count x 3
        if result.size == np.sum(~self.dof.reshape(-1)):  # fixations_count
            full_array = np.zeros(3 * self._count)
            fixed_dof_indices = np.arange(3 * self._count)[~self.dof.reshape(-1)]
            full_array[fixed_dof_indices] = result
            return full_array.reshape(self._count, 3)
            
        raise ValueError(f"{name} cannot be reshaped to ({self._count}, 3), got shape {result.shape}")
    
    def _initialize(self, initial_coordinates, dof, loads, displacements, reactions, resisting_forces):
        """Initialize all attributes with proper validation."""
        # Handle coordinates first to establish count
        if initial_coordinates is not None:
            # Convert to numpy array if needed
            initial_coords = initial_coordinates if isinstance(initial_coordinates, np.ndarray) else np.array(initial_coordinates, dtype=float)
            assert len(initial_coords.shape) == 2 and initial_coords.shape[1] == 3, "initial_coordinates must be a 2D array with 3 columns"
            self._count = len(initial_coords)
            self._initial_coordinates = initial_coords
        
        # Handle degrees of freedom
        if dof is not None:
            self._dof = self._check_array(dof, "dof")
            self._fixations_count = np.sum(~self._dof.flatten()) # Compute number of fixed DOFs

        # Initialize state arrays
        self._loads = self._check_array(loads, "loads")
        self._displacements = self._check_array(displacements, "displacements")
        self._reactions = self._check_array(reactions, "reactions")
        self._resisting_forces = self._check_array(resisting_forces, "resisting_forces")
        self._residual = np.zeros((self._count, 3), dtype=float)
    
    # READ Only properties
    @property
    def initial_coordinates(self) -> np.ndarray:
        """[m] - shape (nodes_count, 3) - Initial nodal coordinates"""
        return self._initial_coordinates
    
    @property
    def coordinates(self) -> np.ndarray:
        """[m] - shape (nodes_count, 3) - Current nodal coordinates"""
        return self._initial_coordinates + self._displacements
    
    @property
    def dof(self) -> np.ndarray:
        """[-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)"""
        return self._dof
    
    @property
    def count(self) -> int:
        """Number of nodes"""
        return self._count
    
    @property
    def fixations_count(self) -> int:
        """Number of fixed degrees of freedom"""
        return self._fixations_count
    

    @property
    def loads(self) -> np.ndarray:
        """[N] - shape (nodes_count, 3) - External loads applied to nodes"""
        return self._loads
    
    
    @property
    def displacements(self) -> np.ndarray:
        """[m] - shape (nodes_count, 3) - Nodal displacements"""
        return self._displacements
    
    
    @property
    def reactions(self) -> np.ndarray:
        """[N] - shape (nodes_count, 3) - Support reactions"""
        return self._reactions
    
    
    @property
    def resisting_forces(self) -> np.ndarray:
        """[N] - shape (nodes_count, 3) - Internal resisting forces at nodes"""
        return self._resisting_forces
    
    
    @property
    def residual(self) -> np.ndarray:
        """[N] - shape (nodes_count, 3) - Out of balance loads"""
        return self._loads + self._reactions - self._resisting_forces
        

    # Public Methods
    def copy_and_update(self, loads: np.ndarray, displacements: np.ndarray, reactions: np.ndarray, resisting_forces: np.ndarray) -> 'FEM_Nodes':
        """Create a copy of this instance and update its state.
        
        Args:
            loads: [N] - shape (nodes_count, 3) or (3*nodes_count,) - External loads
            displacements: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Support reactions
            resisting_forces: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Internal resisting forces
        """
        # Reshape inputs if needed
        loads = self._reshape_array(loads, "loads")
        displacements = self._reshape_array(displacements, "displacements")
        reactions = self._reshape_array(reactions, "reactions")
        resisting_forces = self._reshape_array(resisting_forces, "resisting_forces")
        
        return FEM_Nodes(
            initial_coordinates=self._initial_coordinates.copy(),
            dof=self._dof.copy(),
            loads=loads,
            displacements=displacements,
            reactions=reactions,
            resisting_forces=resisting_forces
        )
        
    def copy_and_add(self, loads_increment: np.ndarray, displacements_increment: np.ndarray, 
                     reactions_increment: np.ndarray, resisting_forces_increment: np.ndarray) -> 'FEM_Nodes':
        """Create a copy of this instance and add increments to its state.
        
        Args:
            loads_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Load increments
            displacements_increment: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Displacement increments
            reactions_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Reaction increments
            resisting_forces_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Resisting forces increments
        """
        # Reshape inputs if needed
        loads_inc = self._reshape_array(loads_increment, "loads_increment")
        displacements_inc = self._reshape_array(displacements_increment, "displacements_increment")
        reactions_inc = self._reshape_array(reactions_increment, "reactions_increment")
        resisting_forces_inc = self._reshape_array(resisting_forces_increment, "resisting_forces_increment")
        
        return FEM_Nodes(
            initial_coordinates=self._initial_coordinates.copy(),
            dof=self._dof.copy(),
            loads=self._loads + loads_inc,
            displacements=self._displacements + displacements_inc,
            reactions=self._reactions + reactions_inc,
            resisting_forces=self._resisting_forces + resisting_forces_inc
        )