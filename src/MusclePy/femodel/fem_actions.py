import numpy as np


class FEM_Actions:
    def __init__(self, loads=None, delta_free_lengths=None, n=None, b=None):
        """Initialize FEM_Actions with either:
        - Explicit loads and delta_free_lengths arrays
        - Size parameters n (for nodes) and b (for elements) to create zero arrays
        
        Args:
            n: Number of nodes to create zero loads array of shape (n, 3). Only used if loads is None.
            b: Number of elements to create zero delta_free_lengths array of shape (b,). Only used if delta_free_lengths is None.
            loads: Explicit loads array of shape (n, 3)
            delta_free_lengths: Explicit delta_free_lengths array of shape (b,)
        """
        # Handle loads initialization
        if loads is not None:
            self.loads = np.array(loads, dtype=float)
            assert len(self.loads.shape) == 2 and self.loads.shape[1] == 3, f"loads should have shape (n, 3) but got {self.loads.shape}"
        elif n is not None:
            self.loads = np.zeros((n, 3), dtype=float)
        else:
            self.loads = np.array([], dtype=float).reshape((0, 3))
            
        # Handle delta_free_lengths initialization
        if delta_free_lengths is not None:
            self.delta_free_lengths = np.array(delta_free_lengths, dtype=float)
            assert len(self.delta_free_lengths.shape) == 1, f"delta_free_lengths should be 1D array but got shape {self.delta_free_lengths.shape}"
        elif b is not None:
            self.delta_free_lengths = np.zeros(b, dtype=float)
        else:
            self.delta_free_lengths = np.array([], dtype=float)
