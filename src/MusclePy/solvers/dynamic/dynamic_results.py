"""
Dynamic modal analysis results class for structural dynamics.

This module provides a class to store the results of dynamic modal analysis
including natural frequencies and mode shapes.
"""

import numpy as np

class DynamicResults:
    """
    This class stores the results of the dynamic modal analysis of a structure.
    
    It contains natural frequencies and corresponding mode shapes for a structure
    with a given mass distribution and stiffness.
    """

    def __init__(self, frequencies, mode_shapes, total_mode_shapes=None, max_frequencies=None):
        """
        Initialize a DynamicResults object that stores the results of modal analysis.
        
        Args:
            frequencies: np.ndarray: Natural frequencies in Hz
            mode_shapes: np.ndarray: Mode shapes corresponding to the natural frequencies (only free DOFs)
            total_mode_shapes: np.ndarray: Mode shapes including zeros for fixed DOFs (optional)
            max_frequencies: int: Maximum number of frequencies computed (optional)
        """
        self.frequencies = frequencies  # Natural frequencies in Hz
        self.mode_shapes = mode_shapes  # Mode shapes corresponding to the natural frequencies 
        
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
    
    def get_mode(self, index):
        """
        Get a specific mode shape.
        
        Args:
            index: int: Index of the mode (0-based)
            
        Returns:
            np.ndarray: Mode shape corresponding to the requested index
        """
        if index < 0 or index >= self.mode_count:
            raise IndexError(f"Mode index {index} out of range (0-{self.mode_count-1})")
        
        return self.mode_shapes[:, index]
    