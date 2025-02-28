
import numpy as np


class FEM_Structure:
    def __init__(self, nodes=None, elements=None, actions=None, nodes_results=None, elements_results=None):
        """Python equivalent of C# FEM_Structure class"""
        self.nodes = FEM_Nodes(nodes)  if nodes is not None else FEM_Nodes()
        self.elements = FEM_Elements(elements) if elements is not None else FEM_Elements()

        # Already applied actions (Loads and Prestress) on the structure  
        self.actions = FEM_Actions(actions) if actions is not None else FEM_Actions() 

        # nodes results (from the already applied actions) 
        self.nodes_results = FEM_NodesResults(nodes_results) if nodes_results is not None else FEM_NodesResults()

        # elements results (from the already applied actions) 
        self.elements_results = FEM_ElementsResults(elements_results) if elements_results is not None else FEM_ElementsResults()

