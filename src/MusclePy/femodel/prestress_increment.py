import numpy as np
from MusclePy.femodel.fem_elements import FEM_Elements


class PrestressIncrement:
    """Class representing a prestress increment applied through free length variations.
    
    This class computes:
    1. The axial force in each element that would result from the free length variations assuming all nodes are totally fixed.
    2. The equivalent external loads, to apply on the structure through linear displacement method, 
       that would produce the same effect as the free length variations. 

    references:
    - fig 5: Latteur P., Feron J., Denoël V., 2017, "A design methodology for lattice and tensegrity structures based on a stiffness and volume optimization algorithm using morphological indicators", International Journal of Space Structures, Volume 32, issue: 3-4, p. 226-243.
    
    Attributes:
        elements: FEM_Elements instance containing element properties and current state
        free_length_variation: [m] - shape (elements.count,) - free length variations (imposed by mechanical devices)
        equivalent_tension: [N] - shape (elements.count,) - Axial force in each element
        equivalent_loads: [N] - shape (nodes.count,3) - Equivalent external loads
    """
    
    def __init__(self, elements: FEM_Elements, free_length_variation: np.ndarray = None):
        """Initialize a PrestressIncrement instance.
        
        Args:
            elements: FEM_Elements instance containing element properties and current state
            free_length_variation: [m] - shape (elements.count,) - free length variations (imposed by mechanical devices)
        """
        # Validate inputs
        assert isinstance(elements, FEM_Elements), "elements must be an instance of FEM_Elements"
        free_length_variation = elements._check_and_reshape_array(free_length_variation, "free_length_variation")

        # Modify the free length of the elements via mechanical devices
        self.free_length_variation = free_length_variation
        self.elements = elements.copy_and_add(free_length_variation=free_length_variation) 

        # Initialize equivalent loads and tensions
        self.equivalent_loads = np.zeros((elements.nodes.count, 3))  # Shape (nodes_count, 3)
        self.equivalent_tension = np.zeros((elements.count,))  # Shape (elements_count,)
        
        # Compute equivalent tension and loads
        self._compute_equivalent_tension_and_loads()
    
    def _compute_equivalent_tension_and_loads(self):
        """Compute equivalent tension and loads from free length variations."""
        d_l0 = self.free_length_variation
        Ke = 1/self.elements.flexibility # [N/m] - stiffness of the elements = EA/(new_Lfree)
        cosines = self.elements.direction_cosines
        end_nodes = self.elements.end_nodes
        
        # 1) Compute the tension
        # t = EA/Lfree * (-d_l0). A lengthening d_l0 (+) creates a compression force (-), supposing all nodes are fixed.
        self.equivalent_tension = Ke * -d_l0
        
        # 2) Compute the equivalent prestress loads
        for i in range(self.elements.count):
            cx, cy, cz = cosines[i]
            n0, n1 = end_nodes[i]  # Get start and end nodes
            
            # Apply forces to start node (negative)
            self.equivalent_loads[n0] += -self.equivalent_tension[i] * np.array([-cx, -cy, -cz])
            
            # Apply forces to end node (positive)
            self.equivalent_loads[n1] += -self.equivalent_tension[i] * np.array([cx, cy, cz])
