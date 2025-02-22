
import numpy as np


class Twin_Structure:
    def __init__(self, nodes=None, elements=None, additional=None, applied=None, initial_nodes_results=None, initial_elements_results=None):
        """Python equivalent of C# Twin_Structure class"""
        self.nodes = Twin_Nodes(nodes)  if nodes is not None else Twin_Nodes()
        self.elements = Twin_Elements(elements) if elements is not None else Twin_Elements()

        # Additional actions (Loads and Prestress) on the structure
        self.additional = Twin_Actions(additional) if additional is not None else Twin_Actions()

        # Already applied actions (Loads and Prestress) on the structure  
        self.applied = Twin_Actions(applied) if applied is not None else Twin_Actions() 

        # Previous nodes results (from the already applied actions) 
        self.initial_nodes_results = Twin_NodesResults(initial_nodes_results) if initial_nodes_results is not None else Twin_NodesResults()

        # Previous elements results (from the already applied actions) 
        self.initial_elements_results = Twin_ElementsResults(initial_elements_results) if initial_elements_results is not None else Twin_ElementsResults()

