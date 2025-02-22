import numpy as np


class FEM_Elements:
    def __init__(self, type=None, end_nodes=None, areas=None, young_moduli=None, initial_free_lengths=None):
        """Python equivalent of C# FEM_Elements class"""
        # shape (ElementsCount, )
        self.type = np.array(type, dtype=int) if type is not None else np.array([])  

         # shape (ElementsCount, 2)
        self.end_nodes = np.array(end_nodes, dtype=int) if end_nodes is not None else np.array([[],[]]) 

        # [mm²] - shape (ElementsCount, 2) - Area in Compression and Area in Tension of the Elements
        self.areas = np.array(areas, dtype=float) if areas is not None else np.array([[],[]]) 

        # [MPa] - shape (ElementsCount, 2) - Young Moduli in Compression and in Tension of the Elements
        self.young_moduli = np.array(young_moduli, dtype=float) if young_moduli is not None else np.array([[],[]]) 

        # # shape (ElementsCount, ) - Free Length of the Elements before any analysis
        # self.initial_free_lengths = np.array(initial_free_lengths, dtype=float) if initial_free_lengths is not None else np.array([[],[]])  



    def count(self):
        return self.areas.shape[0]

    def set_initial_free_lengths(self, initial_free_lengths):