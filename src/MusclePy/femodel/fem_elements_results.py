import numpy as np


class FEM_ElementsResults:
    def __init__(self, tension=None, elastic_elongation=None, b=None):
        """Initialize FEM_ElementsResults with either:
        - Explicit arrays for tension and elastic_elongation
        - Size parameter b to create zero arrays of shape (b,)
        
        Args:
            tension: Explicit tension array of shape (b,)
            elastic_elongation: Explicit elastic_elongation array of shape (b,)
            b: Number of elements to create zero arrays of shape (b,). Only used if corresponding array is None.
        """
        # Handle tension initialization
        if tension is not None:
            self.tension = np.array(tension, dtype=float)
            assert len(self.tension.shape) == 1, f"tension should be 1D array but got shape {self.tension.shape}"
        elif b is not None:
            self.tension = np.zeros(b, dtype=float)
        else:
            self.tension = np.array([], dtype=float)
            
        # Handle elastic_elongation initialization
        if elastic_elongation is not None:
            self.elastic_elongation = np.array(elastic_elongation, dtype=float)
            assert len(self.elastic_elongation.shape) == 1, f"elastic_elongation should be 1D array but got shape {self.elastic_elongation.shape}"
        elif b is not None:
            self.elastic_elongation = np.zeros(b, dtype=float)
        else:
            self.elastic_elongation = np.array([], dtype=float)
