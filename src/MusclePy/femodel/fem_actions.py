import clr
import System
from System import Array
import numpy as np

# Add references to the C# assemblies
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_Actions as CS_FEM_Actions

class FEM_Actions:
    def __init__(self):
        """Python equivalent of C# FEM_Actions class"""
        self.loads = np.array([], dtype=float)  # [N] - shape (NodesCount,3)
        self.delta_free_lengths = np.array([], dtype=float)  # [m] - shape (ElementsCount,)

    def to_cs_actions(self) -> CS_FEM_Actions:
        """Convert Python FEM_Actions to C# FEM_Actions"""
        cs_actions = CS_FEM_Actions()
        cs_actions.Loads = self._to_2d_array(self.loads, float)
        cs_actions.Delta_FreeLengths = Array[float](self.delta_free_lengths.flatten())
        return cs_actions

    @staticmethod
    def from_cs_actions(cs_actions: CS_FEM_Actions):
        """Create Python FEM_Actions from C# FEM_Actions"""
        py_actions = FEM_Actions()
        py_actions.loads = np.array(list(cs_actions.Loads)).reshape(-1, 3)
        py_actions.delta_free_lengths = np.array(list(cs_actions.Delta_FreeLengths))
        return py_actions

    def _to_2d_array(self, arr: np.ndarray, dtype) -> Array[Array[dtype]]:
        """Convert numpy 2D array to C# 2D array"""
        if arr.size == 0:
            return Array[Array[dtype]]([])
        rows, cols = arr.shape
        result = Array[Array[dtype]](rows)
        for i in range(rows):
            result[i] = Array[dtype](arr[i])
        return result
