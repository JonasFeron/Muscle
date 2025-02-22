import numpy as np

class Twin_StructureResults:
    def __init__(self, total=None, total_nodes=None, total_elements=None):
        """Python equivalent of C# Twin_StructureResults class"""
        # Total actions (Loads and Prestress) on the structure
        self.total = Twin_Actions(total) if total is not None else Twin_Actions()

        # Total nodes results (displacements, reactions, ... from the total actions)
        self.total_nodes = Twin_NodesResults(total_nodes) if total_nodes is not None else Twin_NodesResults()

        # Total elements results (tensions, elongations, ... from the total actions)
        self.total_elements = Twin_ElementsResults(total_elements) if total_elements is not None else Twin_ElementsResults()


