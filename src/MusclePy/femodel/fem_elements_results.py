import clr
import System
from System import Array
import numpy as np

# Add references to the C# assemblies
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_ElementsResults as CS_FEM_ElementsResults

class FEM_ElementsResults:
    def __init__(self):
        """Python equivalent of C# FEM_ElementsResults class"""
        self.tension = np.array([], dtype=float)  # [N] - shape (ElementsCount,)
        self.elastic_elongation = np.array([], dtype=float)  # [m] - shape (ElementsCount,)

    def to_cs_elements_results(self) -> CS_FEM_ElementsResults:
        """Convert Python FEM_ElementsResults to C# FEM_ElementsResults"""
        cs_elements_results = CS_FEM_ElementsResults()
        cs_elements_results.Tension = Array[float](self.tension.flatten())
        cs_elements_results.ElasticElongation = Array[float](self.elastic_elongation.flatten())
        return cs_elements_results

    @staticmethod
    def from_cs_elements_results(cs_elements_results: CS_FEM_ElementsResults):
        """Create Python FEM_ElementsResults from C# FEM_ElementsResults"""
        py_elements_results = FEM_ElementsResults()
        py_elements_results.tension = np.array(list(cs_elements_results.Tension))
        py_elements_results.elastic_elongation = np.array(list(cs_elements_results.ElasticElongation))
        return py_elements_results
