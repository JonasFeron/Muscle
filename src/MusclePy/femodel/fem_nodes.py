from argparse import ArgumentError
import numpy as np
from typing import Optional

class FEM_Nodes:
    def __init__(self, initial_coordinates=None, dof=None, loads=None, displacements=None, reactions=None, resisting_forces=None):
        """Python equivalent of C# FEM_Nodes class, combining nodes state and results.
        
        The class has four types of attributes (immutable, or mutable (state dependant)) and (provided by the solver, or computed internally):
        1. Immutable attributes (initialized once from C#):
            - initial_coordinates: Initial nodal coordinates
            - dof: Degrees of freedom (support conditions)

        2. Immutable attributes (computed internally):
            - count: Number of nodes
            - fixations_count: Number of fixed DOFs
            
        3. Mutable state attributes (provided by the solver):
            - loads: external loads applied to nodes
            - displacements: Nodal displacements
            - reactions: Support reactions
            - resisting_forces: Internal resisting forces at nodes

        4. Mutable state attributes (computed internally):
            - coordinates: Current nodal coordinates (initial_coordinates + displacements)
            - residual: Out of balance forces (loads - resisting_forces - reactions)
        
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
        
        # Initialize the instance
        self._initialize(initial_coordinates, dof, loads, displacements, reactions, resisting_forces)
    
    def _check_and_reshape_array(self, arr, name) -> np.ndarray:
        """Convert input array to proper numpy array with correct shape and type.
        
        Handles these cases:
        1. None -> zeros array
        2. Shape (nodes_count, 3) -> converted to proper dtype (float or bool)
        3. Shape (3*nodes_count,) -> reshaped to (nodes_count, 3)
        4. Shape (fixations_count,) -> expanded to (nodes_count, 3) for reactions
        
        Args:
            arr: Array to convert
            name: Name of array for error messages and type detection
        """
        if arr is None:
            return np.zeros((self._count, 3), dtype=bool if name == "dof" else float)
            
        # Convert to numpy array with correct dtype
        if not isinstance(arr, np.ndarray):  # if arr is a C# array
            # Handle C# bool array conversion explicitly
            if name == "dof":
                result = np.array(list(arr), dtype=bool)
            else:
                result = np.array(arr, dtype=float, copy=True)
        else:
            result = arr
            
        # Handle correct shape
        if result.shape == (self._count, 3):
            return result
            
        # Try to reshape if it's a flat array
        if result.size == self._count * 3:
            return result.reshape(self._count, 3)
            
        # Special case: reactions array from fixations_count to nodes_count x 3
        if name in ["reactions", "reactions_increment"] and result.size == np.sum(~self.dof.reshape(-1)):
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
            
            # Handle flat array case
            if initial_coords.ndim == 1:
                if len(initial_coords) % 3 == 0:
                    self._count = len(initial_coords) // 3
                    self._initial_coordinates = initial_coords.reshape(self._count, 3)
                else:
                    raise ValueError("initial_coordinates as flat array must have length divisible by 3")
            else: # handle 2D array
                if initial_coords.shape[1] != 3:
                    raise ValueError(f"initial_coordinates as 2D array must have shape (n,3), got shape {initial_coords.shape}")
                self._count = len(initial_coords)
                self._initial_coordinates = initial_coords
        else:  
            raise ArgumentError(f"impossible to initialize FEM_Nodes without initial_coordinates, no initial_coordinates provided")

        # Handle degrees of freedom
        if dof is not None:
            self._dof = self._check_and_reshape_array(dof, "dof")
            self._fixations_count = np.sum(~self._dof.flatten())

        # Initialize state arrays
        self._loads = self._check_and_reshape_array(loads, "loads")
        self._displacements = self._check_and_reshape_array(displacements, "displacements")
        self._reactions = self._check_and_reshape_array(reactions, "reactions")
        self._resisting_forces = self._check_and_reshape_array(resisting_forces, "resisting_forces")
    
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
    def residuals(self) -> np.ndarray:
        """[N] - shape (nodes_count, 3) - Out of balance loads"""
        return self._loads + self._reactions - self._resisting_forces
        

    # Public Methods
    def _create_copy(self, initial_coordinates, dof, loads, displacements, reactions, resisting_forces):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (FEM_Nodes or a child class)
        """
        return self.__class__(
            initial_coordinates=initial_coordinates,
            dof=dof,
            loads=loads,
            displacements=displacements,
            reactions=reactions,
            resisting_forces=resisting_forces
        )
    
    def copy(self) -> 'FEM_Nodes':
        """Create a copy of this instance with the current state.
        
        Returns:
            A new instance with the current state
        """
        return self._create_copy(
            initial_coordinates=self._initial_coordinates.copy(),
            dof=self._dof.copy(),
            loads=self._loads.copy(),
            displacements=self._displacements.copy(),
            reactions=self._reactions.copy(),
            resisting_forces=self._resisting_forces.copy()
        )

    def copy_and_update(self, loads: np.ndarray = None, displacements: np.ndarray = None, reactions: np.ndarray = None, resisting_forces: np.ndarray = None) -> 'FEM_Nodes':
        """Create a copy of this instance and update its state, or use existing state if None.
        
        Args:
            loads: [N] - shape (nodes_count, 3) or (3*nodes_count,) - External loads
            displacements: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Support reactions
            resisting_forces: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Internal resisting forces
        """
        if loads is None: loads = self._loads.copy()
        if displacements is None: displacements = self._displacements.copy()
        if reactions is None: reactions = self._reactions.copy()
        if resisting_forces is None: resisting_forces = self._resisting_forces.copy()
            
        # Reshape inputs if needed
        loads = self._check_and_reshape_array(loads, "loads")
        displacements = self._check_and_reshape_array(displacements, "displacements")
        reactions = self._check_and_reshape_array(reactions, "reactions")
        resisting_forces = self._check_and_reshape_array(resisting_forces, "resisting_forces")
        
        return self._create_copy(
            initial_coordinates=self._initial_coordinates.copy(),
            dof=self._dof.copy(),
            loads=loads,
            displacements=displacements,
            reactions=reactions,
            resisting_forces=resisting_forces
        )
        
    def copy_and_add(self, loads_increment: np.ndarray = None, displacements_increment: np.ndarray = None, 
                     reactions_increment: np.ndarray = None, resisting_forces_increment: np.ndarray = None) -> 'FEM_Nodes':
        """Create a copy of this instance and add increments to its state.
        
        Args:
            loads_increment: [N] - size: 3*nodes.count - Loads increment to add
            displacements_increment: [m] - size: 3*nodes.count - Displacements increment to add
            reactions_increment: [N] - size: 3*nodes.count - Reactions increment to add
            resisting_forces_increment: [N] - size: 3*nodes.count - Resisting forces increment to add
            
        Returns:
            New FEM_Nodes with incremented state
        """
        # Create zero arrays if arguments are None

        loads_increment = self._check_and_reshape_array(loads_increment, "loads_increment")
        displacements_increment = self._check_and_reshape_array(displacements_increment, "displacements_increment")
        reactions_increment = self._check_and_reshape_array(reactions_increment, "reactions_increment")
        resisting_forces_increment = self._check_and_reshape_array(resisting_forces_increment, "resisting_forces_increment")
            
        return self.copy_and_update(
            loads=self._loads + loads_increment,
            displacements=self._displacements + displacements_increment,
            reactions=self._reactions + reactions_increment,
            resisting_forces=self._resisting_forces + resisting_forces_increment
        )
