import unittest
import numpy as np
from MusclePy.femodel.pynodes import PyNodes
from MusclePy.femodel.pyelements import PyElements
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.solvers.svd.main import main_singular_value_decomposition
from MusclePy.solvers.selfstress.modes import localize_self_stress_modes

class TestSelfStressModes(unittest.TestCase):
    """Test cases for the SelfStressModes class with a 2X Snelson structure.
    
    This test verifies the localization of self-stress modes in a 2X Snelson structure
    as described in:
    [1] Aloui, O., Lin, J., Rhode-Barbarigos, L. (2019). A theoretical framework for 
        sensor placement, structural identification and damage detection in tensegrity 
        structures. Smart Materials and Structures.
    """

    def setUp(self):
        """Set up the 2X Snelson structure for testing."""
        # Create nodes
        coordinates = np.array([
            [0, 0, 0],
            [1, 0, -0.2],
            [0.8, 0, 0.8],
            [-0.2, 0, 1],
            [2.2, 0, 1],
            [2, 0, 0]
        ])
        
        # Define DOF (True = free, False = fixed)
        dof = np.array([
            False, False, False,  # Node 0: fixed
            True, False, True,    # Node 1: free in x and z
            True, False, True,    # Node 2: free in x and z
            True, False, True,    # Node 3: free in x and z
            True, False, True,    # Node 4: free in x and z
            True, False, False    # Node 5: free in x only
        ])
        
        nodes = PyNodes(coordinates, dof)
        
        # Create elements
        end_nodes = np.array([
            [0, 1],  # Element 0
            [1, 2],  # Element 1
            [2, 3],  # Element 2
            [0, 3],  # Element 3
            [0, 2],  # Element 4 - strut
            [1, 3],  # Element 5 - strut
            [2, 4],  # Element 6
            [4, 5],  # Element 7
            [1, 5],  # Element 8
            [1, 4],  # Element 9 - strut
            [2, 5]   # Element 10 - strut
        ])
        
        # Set element types (1 for cables, -1 for struts)
        elements_type = np.ones(11)
        elements_type[[4, 5, 9, 10]] = -1  # struts
                
        # Set element properties
        elementsE = np.ones((11,2)) * 70000  # MPa
        elementsA = np.ones(11)
        elementsA[0:3] = 364.4 # struts 
        elementsA[3:11] = 50.3 # cables
        
        # Create elements with types
        elements = PyElements(nodes=nodes, end_nodes=end_nodes, type=elements_type, youngs=elementsE, area=elementsA)
        
        self.structure = PyTruss(nodes, elements)
        
        # Run SVD analysis
        self.svd_results = main_singular_value_decomposition(self.structure)

    def test_localize_self_stress_modes(self):
        """Test the localization of self-stress modes."""
        # Get the self-stress modes from SVD
        Vs_T = self.svd_results.Vs_T

        
        # Apply localization
        localized_modes = localize_self_stress_modes(self.structure,Vs_T)

        expected_localized_modes = np.array([
            [0.60, 0.60, 0.60, 0.60, -0.67, -1.00, 0   , 0   , 0   ,  0   ,  0   ],
            [0   , 0.56, 0   , 0   ,  0   ,  0   , 0.59, 0.64, 0.83, -1.00, -0.83]
        ])

        self.assertTrue(np.allclose(np.abs(localized_modes), np.abs(expected_localized_modes), atol=0.01),
                        f"Expected localized modes:\n{expected_localized_modes}\nGot:\n{localized_modes}")
        

if __name__ == '__main__':
    unittest.main()
