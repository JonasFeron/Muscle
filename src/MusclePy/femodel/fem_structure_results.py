import numpy as np

class FEM_StructureResults:
    def __init__(self, total=None, total_nodes=None, total_elements=None):
        """Python equivalent of C# FEM_StructureResults class"""
        # Total actions (Loads and Prestress) on the structure
        self.total = FEM_Actions(total) if total is not None else FEM_Actions()

        # Total nodes results (displacements, reactions, ... from the total actions)
        self.total_nodes = FEM_NodesResults(total_nodes) if total_nodes is not None else FEM_NodesResults()

        # Total elements results (tensions, elongations, ... from the total actions)
        self.total_elements = FEM_ElementsResults(total_elements) if total_elements is not None else FEM_ElementsResults()


