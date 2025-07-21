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

"""
Dynamic modal analysis results class for structural dynamics.

This module provides a class to store the results of dynamic modal analysis
including natural frequencies and mode shapes.
"""

import numpy as np

class PyResultsDynamic:
    """
    This class stores the results of the dynamic modal analysis of a structure.
    
    It contains natural frequencies and corresponding mode shapes for a structure
    with a given mass distribution and stiffness.
    """

    def __init__(self, frequencies, mode_shapes, mass_matrix):
        """
        Initialize a PyResultsDynamic object that stores the results of modal analysis.
        
        Args:
            frequencies: np.ndarray - shape (n_modes,): Natural frequencies in Hz
            mode_shapes: np.ndarray - shape (n_modes, 3*nodes_count): Mode shapes corresponding to the natural frequencies
            mass_matrix: np.ndarray - shape (3*nodes_count, 3*nodes_count): Mass matrix of the structure
        """
        self.frequencies = frequencies  # Natural frequencies in Hz
        self.mode_shapes = mode_shapes  # Mode shapes corresponding to the natural frequencies 
        self.mass_matrix = mass_matrix  # Mass matrix of the structure
        
    @property
    def angular_frequencies(self):
        """
        Returns:
            np.ndarray: Angular frequencies in rad/s (ω = 2π·f)
        """
        return 2 * np.pi * self.frequencies
    
    @property
    def periods(self):
        """
        Returns:
            np.ndarray: Periods in seconds (T = 1/f)
        """
        return 1 / self.frequencies
    
    @property
    def mode_count(self):
        """
        Returns:
            int: Number of computed modes
        """
        return len(self.frequencies)
    
    @property
    def masses(self):
        """
        Transforms the Mass matrix (3n,3n) into a column vector (3n,), by adding up the entries for each row. 
        Returns:
            np.ndarray: shape(3n,) -  a simplified version of the Mass matrix for visualisation purpose. 
        """
        return np.sum(self.mass_matrix,axis=1) 
    
    