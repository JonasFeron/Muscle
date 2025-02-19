import clr
import System
from System import Array
import numpy as np

# Add references to the C# assemblies
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_Elements as CS_FEM_Elements

class FEM_Elements:
    def __init__(self):
        """Python equivalent of C# FEM_Elements class"""
        self.type = np.array([], dtype=int)  # shape (ElementsCount, )
        self.end_nodes = np.array([], dtype=int)  # shape (ElementsCount, 2)
        self.areas = np.array([], dtype=float)  # [mm²] - shape (ElementsCount, 2) - Area in Compression and Area in Tension of the Elements
        self.young_moduli = np.array([], dtype=float)  # [MPa] - shape (ElementsCount, 2) - Young Modulus in Compression and in Tension of the Elements
        self.initial_free_lengths = np.array([], dtype=float)  # shape (ElementsCount, ) - Free Length of the Elements before any analysis

    def to_cs_elements(self) -> CS_FEM_Elements:
        """Convert Python FEM_Elements to C# FEM_Elements"""
        cs_elements = CS_FEM_Elements()
        cs_elements.Type = Array[int](self.type.flatten())
        cs_elements.EndNodes = self._to_2d_array(self.end_nodes, int)
        cs_elements.Areas = self._to_2d_array(self.areas, float)
        cs_elements.YoungModuli = self._to_2d_array(self.young_moduli, float)
        cs_elements.Initial_FreeLengths = Array[float](self.initial_free_lengths.flatten())
        return cs_elements

    @staticmethod
    def from_cs_elements(cs_elements: CS_FEM_Elements):
        """Create Python FEM_Elements from C# FEM_Elements"""
        py_elements = FEM_Elements()
        py_elements.type = np.array(list(cs_elements.Type))
        py_elements.end_nodes = np.array(list(cs_elements.EndNodes)).reshape(-1, 2)
        py_elements.areas = np.array(list(cs_elements.Areas)).reshape(-1, 2)
        py_elements.young_moduli = np.array(list(cs_elements.YoungModuli)).reshape(-1, 2)
        py_elements.initial_free_lengths = np.array(list(cs_elements.Initial_FreeLengths))
        return py_elements

    def _to_2d_array(self, arr: np.ndarray, dtype) -> Array[Array[dtype]]:
        """Convert numpy 2D array to C# 2D array"""
        if arr.size == 0:
            return Array[Array[dtype]]([])
        rows, cols = arr.shape
        result = Array[Array[dtype]](rows)
        for i in range(rows):
            result[i] = Array[dtype](arr[i])
        return result
