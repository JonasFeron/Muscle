import clr
import System
from System import Array
import numpy as np

# Add references to the C# assemblies
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_NodesResults as CS_FEM_NodesResults

class FEM_NodesResults:
    def __init__(self):
        """Python equivalent of C# FEM_NodesResults class"""
        self.displacements = np.array([], dtype=float)  # [m] - shape (NodesCount,3)
        self.residual = np.array([], dtype=float)  # [N] - shape (NodesCount,3)
        self.reactions = np.array([], dtype=float)  # [N] - shape (NodesCount,3)

    def to_cs_nodes_results(self) -> CS_FEM_NodesResults:
        """Convert Python FEM_NodesResults to C# FEM_NodesResults"""
        cs_nodes_results = CS_FEM_NodesResults()
        cs_nodes_results.Displacements = self._to_2d_array(self.displacements, float)
        cs_nodes_results.Residual = self._to_2d_array(self.residual, float)
        cs_nodes_results.Reactions = self._to_2d_array(self.reactions, float)
        return cs_nodes_results

    @staticmethod
    def from_cs_nodes_results(cs_nodes_results: CS_FEM_NodesResults):
        """Create Python FEM_NodesResults from C# FEM_NodesResults"""
        py_nodes_results = FEM_NodesResults()
        py_nodes_results.displacements = np.array(list(cs_nodes_results.Displacements)).reshape(-1, 3)
        py_nodes_results.residual = np.array(list(cs_nodes_results.Residual)).reshape(-1, 3)
        py_nodes_results.reactions = np.array(list(cs_nodes_results.Reactions)).reshape(-1, 3)
        return py_nodes_results

    def _to_2d_array(self, arr: np.ndarray, dtype) -> Array[Array[dtype]]:
        """Convert numpy 2D array to C# 2D array"""
        if arr.size == 0:
            return Array[Array[dtype]]([])
        rows, cols = arr.shape
        result = Array[Array[dtype]](rows)
        for i in range(rows):
            result[i] = Array[dtype](arr[i])
        return result
