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
from MusclePy.femodel.pyelements import PyElements
from MusclePy.femodel.pynodes import PyNodes
from MusclePy.solvers.dr.py_nodes_dr import PyNodesDR


class PyElementsDR(PyElements):
    """
    Extension of PyElements with Dynamic Relaxation specific attributes.
    
    Attributes:
        All attributes from PyElements
        local_geometric_stiffness_matrices: List of local geometric stiffness matrices
    """
    
    def __init__(self, elements_or_nodes, type=None, end_nodes=None, area=None, youngs=None, 
                 free_length=None, tension=None):
        """Initialize a PyElementsDR instance.
        
        This constructor accepts either:
        1. A PyElements instance to convert to a PyElementsDR instance
        2. A PyNodes (or PyNodesDR) instance plus all parameters (legacy constructor)
        
        Args:
            elements_or_nodes: Either a PyElements instance or a PyNodes (or PyNodesDR) instance
            type: [-] - shape (elements_count,) - Type of elements (-1 for struts, 1 for cables)
            end_nodes: [-] - shape (elements_count, 2) - Indices of end nodes
            area: [mm²] - shape (elements_count,) - Cross-section area of elements
            youngs: [MPa] - shape (elements_count, 2) - Young's moduli for compression and tension
            free_length: [m] - shape (elements_count,) - Free length of elements
            tension: [N] - shape (elements_count,) - Current tension in elements
        """
        # Check if the first argument is a PyElements instance
        if isinstance(elements_or_nodes, PyElements):
            elements = elements_or_nodes
            
            # Assert that all other arguments are None when a PyElements instance is passed
            assert all(arg is None for arg in [type, end_nodes, area, youngs, free_length, tension]), \
                "When passing a PyElements instance, all other arguments must be None"

            # Call parent class constructor with the properties from the PyElements instance
            super().__init__(
                elements.nodes,
                elements.type,
                elements.end_nodes,
                elements.area,
                elements.youngs,
                elements.free_length,
                elements.tension
            )
        else:
            # Assert that the first argument is a PyNodes or PyNodesDR instance
            assert isinstance(elements_or_nodes, (PyNodes, PyNodesDR)), "First argument must be either a PyElements, PyNodes, or PyNodesDR instance"
            nodes = elements_or_nodes
            # Call parent class constructor with the provided parameters
            super().__init__(nodes, type, end_nodes, area, youngs, free_length, tension)
        
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
    
    def _create_copy(self, nodes, type, end_nodes, area, youngs, free_length, tension):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (PyElementsDR or a child class)
        """
        return self.__class__(
            nodes,
            type=type,
            end_nodes=end_nodes,
            area=area,
            youngs=youngs,
            free_length=free_length,
            tension=tension
        )
    
    def copy_and_update(self, nodes=None, free_length=None) -> 'PyElementsDR':
        """Create a copy of this instance and update its state.
        
        Args:
            nodes: A PyNodes or PyNodesDR instance
            free_length: [m] - shape (elements_count,) - Free length of elements
            
        Returns:
            A new instance with the updated state
        """
        # Use current values if not provided
        new_nodes = self.nodes if nodes is None else nodes
        free_length = self.free_length if free_length is None else free_length
        
        # Create a new instance with the updated state
        return self._create_copy(
            new_nodes,
            self.type.copy(),
            self.end_nodes.copy(),
            self.area.copy(),
            self.youngs.copy(),
            free_length,
            self.tension.copy()
        )
