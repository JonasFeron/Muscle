import clr
import System
from System import Array
import numpy as np

# Add references to the C# assemblies
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_StructureResults as CS_FEM_StructureResults

# Import local Python classes
from .fem_actions import FEM_Actions
from .fem_nodes_results import FEM_NodesResults
from .fem_elements_results import FEM_ElementsResults

class FEM_StructureResults:
    def __init__(self):
        """Python equivalent of C# FEM_StructureResults class"""
        self.total = FEM_Actions()  # Total actions (Loads and Prestress) on the structure
        self.total_nodes = FEM_NodesResults()  # Total nodes results (displacements, reactions, ... from the total actions)
        self.total_elements = FEM_ElementsResults()  # Total elements results (tensions, elongations, ... from the total actions)

    def to_cs_results(self) -> CS_FEM_StructureResults:
        """Convert Python FEM_StructureResults to C# FEM_StructureResults"""
        cs_results = CS_FEM_StructureResults()
        cs_results.Total = self.total
        cs_results.TotalNodes = self.total_nodes
        cs_results.TotalElements = self.total_elements
        return cs_results

    @staticmethod
    def from_cs_results(cs_results: CS_FEM_StructureResults):
        """Create Python FEM_StructureResults from C# FEM_StructureResults"""
        py_results = FEM_StructureResults()
        py_results.total = cs_results.Total
        py_results.total_nodes = cs_results.TotalNodes
        py_results.total_elements = cs_results.TotalElements
        return py_results
