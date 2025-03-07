import numpy as np
from MusclePy.femodel.fem_nodes import FEM_Nodes
from typing import Optional


class Nodes_DR(FEM_Nodes):
    """
    Extension of FEM_Nodes with Dynamic Relaxation specific attributes.

    FEM_Nodes class has four types of attributes (immutable, or mutable (state dependant)) and (provided by the solver, or computed internally):
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

    This class adds the necessary attributes for performing the Dynamic Relaxation on a structure:
        3. Additional mutable state attributes (provided by the solver):
            - velocity: Nodal velocities
            - mass: Fictitious masses associated with each node

        4. Additional mutable state attributes (computed internally):
            - kinetic_energy: Computed kinetic energy at each node (0.5 * mass * velocity * velocity)
    
    These attributes are used in the Dynamic Relaxation method as described in:
    [1] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm
    [2] Barnes, 1999, Form finding and analysis of tension structures by dynamic relaxation
    """
    def __init__(self, initial_coordinates=None, dof=None, loads=None, displacements=None, reactions=None, resisting_forces=None,
                 velocity=None, mass=None):
        """
        Initialize a Nodes_DR instance either from an existing FEM_Nodes instance
        or from individual parameters.
        
        Args:
            nodes: Existing FEM_Nodes instance to extend
            initial_coordinates: [m] - shape (nodes_count, 3) - Initial nodal coordinates
            dof: [-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)
            loads: [N] - shape (nodes_count, 3) - External loads applied to nodes
            displacements: [m] - shape (nodes_count, 3) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) - Support reactions
            resisting_forces: [N] - shape (nodes_count, 3) - Internal resisting forces at nodes
            velocity: [m/s] - shape (nodes_count, 3) - Nodal velocities
            mass: [kg] - shape (nodes_count, 3) - Fictitious masses associated with each node
        """
        super().__init__(
                initial_coordinates=initial_coordinates,
                dof=dof,
                loads=loads,
                displacements=displacements,
                reactions=reactions,
                resisting_forces=resisting_forces
            )
        
        # Initialize DR-specific attributes
        self._velocity = np.zeros((self.count, 3), dtype=float)
        self._mass = np.zeros((self.count, 3), dtype=float)
        
        # Set velocity and mass if provided
        if velocity is not None:
            self._velocity = self._check_and_reshape_array(velocity, "velocity")
        
        if mass is not None:
            self._mass = self._check_and_reshape_array(mass, "mass")
    
    @property
    def velocity(self) -> np.ndarray:
        """[m/s] - shape (nodes_count, 3) - Nodal velocities"""
        return self._velocity
    
    @property
    def mass(self) -> np.ndarray:
        """[kg] - shape (nodes_count, 3) - Fictitious masses associated with each node"""
        return self._mass
    
    @property
    def kinetic_energy(self) -> np.ndarray:
        """[J] - shape (nodes_count, 3) - Kinetic energy at each node"""
        return 0.5 * self._mass * self._velocity * self._velocity
    
    @property
    def total_kinetic_energy(self) -> float:
        """[J] - Total kinetic energy in the structure"""
        # Sum kinetic energy only for free DOFs
        is_dof_free = self.dof.reshape(-1)
        ke_vector = self.kinetic_energy.reshape(-1)
        return np.sum(ke_vector[is_dof_free])
    
    def copy(self) -> 'Nodes_DR':
        """Create a copy of this instance with the current state.
        
        Returns:
            A new Nodes_DR instance with the current state
        """
        return Nodes_DR(
            initial_coordinates=self._initial_coordinates.copy(),
            dof=self._dof.copy(),
            loads=self._loads.copy(),
            displacements=self._displacements.copy(),
            reactions=self._reactions.copy(),
            resisting_forces=self._resisting_forces.copy(),
            velocity=self._velocity.copy(),
            mass=self._mass.copy()
        )
    
    def copy_and_update(self, loads: np.ndarray = None, displacements: np.ndarray = None, 
                        reactions: np.ndarray = None, resisting_forces: np.ndarray = None,
                        velocity: np.ndarray = None, mass: np.ndarray = None) -> 'Nodes_DR':
        """Create a copy of this instance and update its state, or use existing state if None.
        
        Args:
            loads: [N] - shape (nodes_count, 3) or (3*nodes_count,) - External loads
            displacements: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Support reactions
            resisting_forces: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Internal resisting forces
            velocity: [m/s] - shape (nodes_count, 3) or (3*nodes_count,) - Nodal velocities
            mass: [kg] - shape (nodes_count, 3) or (3*nodes_count,) - Fictitious masses
        """
        # Create base copy with updated FEM_Nodes attributes
        base_copy = super().copy_and_update(loads, displacements, reactions, resisting_forces)
        
        # Create Nodes_DR instance from the base copy
        dr_copy = Nodes_DR(nodes=base_copy)
        
        # Update DR-specific attributes
        if velocity is not None:
            dr_copy.velocity = velocity
        else:
            dr_copy.velocity = self._velocity.copy()
            
        if mass is not None:
            dr_copy.mass = mass
        else:
            dr_copy.mass = self._mass.copy()
            
        return dr_copy
    
    def copy_and_add(self, loads_increment: np.ndarray = None, displacements_increment: np.ndarray = None, 
                    reactions_increment: np.ndarray = None, resisting_forces_increment: np.ndarray = None,
                    velocity_increment: np.ndarray = None, mass_increment: np.ndarray = None) -> 'Nodes_DR':
        """Create a copy of this instance and add increments to its state.
        
        Args:
            loads_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Loads increment
            displacements_increment: [m] - shape (nodes_count, 3) or (3*nodes_count,) - Displacements increment
            reactions_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Reactions increment
            resisting_forces_increment: [N] - shape (nodes_count, 3) or (3*nodes_count,) - Resisting forces increment
            velocity_increment: [m/s] - shape (nodes_count, 3) or (3*nodes_count,) - Velocity increment
            mass_increment: [kg] - shape (nodes_count, 3) or (3*nodes_count,) - Mass increment
        """
        # Create base copy with incremented FEM_Nodes attributes
        base_copy = super().copy_and_add(loads_increment, displacements_increment, reactions_increment, resisting_forces_increment)
        
        # Create Nodes_DR instance from the base copy
        dr_copy = Nodes_DR(nodes=base_copy)
        
        # Set DR-specific attributes with increments
        if velocity_increment is not None:
            velocity_increment = self._check_and_reshape_array(velocity_increment, "velocity_increment")
            dr_copy.velocity = self._velocity + velocity_increment
        else:
            dr_copy.velocity = self._velocity.copy()
            
        if mass_increment is not None:
            mass_increment = self._check_and_reshape_array(mass_increment, "mass_increment")
            dr_copy.mass = self._mass + mass_increment
        else:
            dr_copy.mass = self._mass.copy()
            
        return dr_copy
    
    def compute_residual(self):
        """Compute the residual forces (out of balance loads)"""
        self._residual = self._loads + self._reactions - self._resisting_forces
        return self._residual
