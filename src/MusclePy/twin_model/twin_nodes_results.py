import numpy as np

class Twin_NodesResults:
    def __init__(self):
        """Python equivalent of C# Twin_NodesResults class"""
        self.displacements = np.array([], dtype=float)  # [m] - shape (NodesCount,3)
        self.residual = np.array([], dtype=float)  # [N] - shape (NodesCount,3)
        self.reactions = np.array([], dtype=float)  # [N] - shape (NodesCount,3)

