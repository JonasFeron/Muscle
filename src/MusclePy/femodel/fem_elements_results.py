import numpy as np

class FEM_ElementsResults:
    def __init__(self, tension=None, elastic_elongation=None):
        """Python equivalent of C# FEM_ElementsResults class"""
        self.tension = np.array(tension, dtype=float) if tension is not None else np.array([])  # [N] - shape (ElementsCount,)
        self.elastic_elongation = np.array(elastic_elongation, dtype=float) if elastic_elongation is not None else np.array([])  # [m] - shape (ElementsCount,)

