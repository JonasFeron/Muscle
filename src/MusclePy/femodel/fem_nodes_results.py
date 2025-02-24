import numpy as np


class FEM_NodesResults:
    def __init__(self, displacements=None, residual=None, reactions=None, n=None):
        """Initialize FEM_NodesResults with either:
        - Explicit arrays for displacements, residual, and reactions
        - Size parameter n to create zero arrays of shape (n, 3)
        
        Args:
            displacements: Explicit displacements array of shape (n, 3)
            residual: Explicit residual array of shape (n, 3)
            reactions: Explicit reactions array of shape (n, 3)
            n: Number of nodes to create zero arrays of shape (n, 3). Only used if corresponding array is None.
        """
        # Handle displacements initialization
        if displacements is not None:
            self.displacements = np.array(displacements, dtype=float)
            assert len(self.displacements.shape) == 2 and self.displacements.shape[1] == 3, f"displacements should have shape (n, 3) but got {self.displacements.shape}"
        elif n is not None:
            self.displacements = np.zeros((n, 3), dtype=float)
        else:
            self.displacements = np.array([], dtype=float).reshape((0, 3))
            
        # Handle residual initialization
        if residual is not None:
            self.residual = np.array(residual, dtype=float)
            assert len(self.residual.shape) == 2 and self.residual.shape[1] == 3, f"residual should have shape (n, 3) but got {self.residual.shape}"
        elif n is not None:
            self.residual = np.zeros((n, 3), dtype=float)
        else:
            self.residual = np.array([], dtype=float).reshape((0, 3))
            
        # Handle reactions initialization
        if reactions is not None:
            self.reactions = np.array(reactions, dtype=float)
            assert len(self.reactions.shape) == 2 and self.reactions.shape[1] == 3, f"reactions should have shape (n, 3) but got {self.reactions.shape}"
        elif n is not None:
            self.reactions = np.zeros((n, 3), dtype=float)
        else:
            self.reactions = np.array([], dtype=float).reshape((0, 3))
