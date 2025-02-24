
import numpy as np


class FEM_Structure:
    def __init__(self, nodes=None, elements=None, additional=None, applied=None, initial_nodes_results=None, initial_elements_results=None):
        """Python equivalent of C# FEM_Structure class"""
        self.nodes = FEM_Nodes(nodes)  if nodes is not None else FEM_Nodes()
        self.elements = FEM_Elements(elements) if elements is not None else FEM_Elements()

        # Additional actions (Loads and Prestress) on the structure
        self.additional = FEM_Actions(additional) if additional is not None else FEM_Actions()

        # Already applied actions (Loads and Prestress) on the structure  
        self.applied = FEM_Actions(applied) if applied is not None else FEM_Actions() 

        # Previous nodes results (from the already applied actions) 
        self.initial_nodes_results = FEM_NodesResults(initial_nodes_results) if initial_nodes_results is not None else FEM_NodesResults()

        # Previous elements results (from the already applied actions) 
        self.initial_elements_results = FEM_ElementsResults(initial_elements_results) if initial_elements_results is not None else FEM_ElementsResults()

