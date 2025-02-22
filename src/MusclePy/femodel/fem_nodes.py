
import numpy as np


class FEM_Nodes:
    def __init__(self, coordinates=None, dof=None):
        """Python equivalent of C# FEM_Nodes class"""
        # Nodal coordinates - shape (NodesCount, 3)
        self.coordinates = np.array(coordinates, dtype=float) if coordinates is not None else np.array([])

        # Supports
        # [bool] - shape (3NodesCount,). Each DegreeOfFreedom can be fixed (False) or free (True). Each point i is associated to its X DOF (3i), Y DOF (3i+1), Z DOF (3i+2). 
        self.dof = np.array(dof, dtype=bool) if dof is not None else np.array([])




