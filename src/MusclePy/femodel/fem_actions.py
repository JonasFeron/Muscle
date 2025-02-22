import numpy as np


class FEM_Actions:
    def __init__(self, loads=None, delta_free_lengths=None):
        """Python equivalent of C# FEM_Actions class"""
        self.loads = np.array(loads, dtype=float) if loads is not None else np.array([[],[],[]])  # [N] - shape (NodesCount,3)
        self.delta_free_lengths = np.array(delta_free_lengths, dtype=float) if delta_free_lengths is not None else np.array([])  # [m] - shape (ElementsCount,)
        
