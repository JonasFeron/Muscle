import clr
import System
from System import Array
import numpy as np

# Add references to the C# assemblies
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_Structure as CS_FEM_Structure

# Import local Python classes
from .fem_nodes import FEM_Nodes
from .fem_elements import FEM_Elements
from .fem_actions import FEM_Actions
from .fem_nodes_results import FEM_NodesResults
from .fem_elements_results import FEM_ElementsResults

class FEM_Structure:
    def __init__(self):
        """Python equivalent of C# FEM_Structure class"""
        self.nodes = FEM_Nodes()  # Updated to use Python FEM_Nodes
        self.elements = FEM_Elements()
        self.additional = FEM_Actions()  # Additional actions (Loads and Prestress) on the structure
        self.applied = FEM_Actions()  # Already applied actions (Loads and Prestress) on the structure
        self.initial_nodes_results = FEM_NodesResults()  # Previous nodes results (from the already applied actions)
        self.initial_elements_results = FEM_ElementsResults()  # Previous elements results (from the already applied actions)

    def to_cs_structure(self) -> CS_FEM_Structure:
        """Convert Python FEM_Structure to C# FEM_Structure"""
        cs_structure = CS_FEM_Structure()
        cs_structure.Nodes = self.nodes
        cs_structure.Elements = self.elements
        cs_structure.Additional = self.additional
        cs_structure.Applied = self.applied
        cs_structure.InitialNodesResults = self.initial_nodes_results
        cs_structure.InitialElementsResults = self.initial_elements_results
        return cs_structure

    @staticmethod
    def from_cs_structure(cs_structure: CS_FEM_Structure):
        """Create Python FEM_Structure from C# FEM_Structure"""
        py_structure = FEM_Structure()
        py_structure.nodes = cs_structure.Nodes
        py_structure.elements = cs_structure.Elements
        py_structure.additional = cs_structure.Additional
        py_structure.applied = cs_structure.Applied
        py_structure.initial_nodes_results = cs_structure.InitialNodesResults
        py_structure.initial_elements_results = cs_structure.InitialElementsResults
        return py_structure
