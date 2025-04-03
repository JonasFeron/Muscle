# Muscle

# Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# List of the contributors to the development of Muscle: see NOTICE file.
# Description and complete License: see NOTICE file.

import numpy as np
from musclepy.femodel.pynodes import PyNodes

class PyNodesDR(PyNodes):
    """
    Extension of PyNodes with Dynamic Relaxation specific attributes.
    
    Attributes:
        All attributes from PyNodes
        velocities: [m/s] - shape (nodes_count, 3) - Nodal velocities
        resisting_forces: [N] - shape (nodes_count, 3) - Resisting forces
    """
    
    def __init__(self, nodes_or_inititialcoordinates, dof=None, loads=None, displacements=None, 
                 reactions=None, resisting_forces=None, velocities=None):
        """Initialize a PyNodesDR instance.
        
        Args:
            nodes_or_coordinates: Either a PyNodes instance or a numpy array of shape (nodes_count, 3) containing nodal coordinates
            dof: [bool] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)
            loads: [N] - shape (nodes_count, 3) - External loads
            displacements: [m] - shape (nodes_count, 3) - Nodal displacements
            reactions: [N] - shape (nodes_count, 3) - Support reactions
            resisting_forces: [N] - shape (nodes_count, 3) - Resisting forces
            velocities: [m/s] - shape (nodes_count, 3) - Nodal velocities
        """
        # Check if the first argument is a PyNodes instance
        if isinstance(nodes_or_inititialcoordinates, PyNodes):
            nodes = nodes_or_inititialcoordinates
            # Call parent class constructor with the PyNodes instance
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
        self._velocities = super()._check_and_reshape_array(velocities, "velocities")

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

    @property
    def resisting_forces(self) -> np.ndarray:
        """[N] - shape (nodes_count, 3) - Resisting forces"""
        return self._resisting_forces
    
    @resisting_forces.setter
    def resisting_forces(self, value):
        """Set resisting forces. Resisting forces are set by PyTrussDR instance once the equilibrium matrix is computed."""
        self._computed_resisting_forces = True
        self._resisting_forces = super()._check_and_reshape_array(value, "resisting_forces")
    
    def compute_reactions(self):
        """Compute support reactions and store them in the _reactions attribute."""
        assert self._computed_resisting_forces, "Impossible to compute reactions, without computing resisting forces first."
        reactions = np.zeros_like(self.resisting_forces)
        where_supports = ~self.dof.astype(bool)
        reactions[where_supports] = self.resisting_forces[where_supports] - self.loads[where_supports] 
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
            A new instance of the appropriate class (PyNodesDR or a child class)
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
    
    def copy(self) -> 'PyNodesDR':
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
    
    def copy_and_update(self, loads=None, displacements=None, velocities=None) -> 'PyNodesDR':
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
        loads = super()._check_and_reshape_array(loads, "loads")
        displacements = super()._check_and_reshape_array(displacements, "displacements")
        velocities = super()._check_and_reshape_array(velocities, "velocities")
        
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
