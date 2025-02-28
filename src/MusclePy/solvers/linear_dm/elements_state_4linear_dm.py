from MusclePy.state_model.nodes_state import Nodes_State
from MusclePy.state_model.elements_state import Elements_State
import numpy as np


class Elements_State_4Linear_DM(Elements_State):
    def __init__(self, elements: FEM_Elements, current_nodes: Nodes_State, 
                 current_action: FEM_Actions = None, current_results: FEM_ElementsResults = None):
        """Initialize Elements_State_4Linear_DM, extending Elements_State with stiffness matrices attributes.
        
        Args:
            Same arguments as Elements_State
        """
        # Call parent class constructor
        super().__init__(elements,current_nodes, current_action, current_results)
        
        # Initialize stiffness matrices attributes
        self.local_material_stiffness_matrices = []  # [N/m] - List(elements.count) of shape (6,6) matrices
        self.local_geometric_stiffness_matrices = []  # [N/m] - List(elements.count) of shape (6,6) matrices

        self._compute_stiffness_matrices()

    def _compute_stiffness_matrices(self):
        """Compute all local stiffness matrices of the elements in the current state.
        
        This method computes:
        1. Local material stiffness matrices
        2. Local geometric stiffness matrices

        """
        # Compute local material stiffness matrices using current element properties (free_length, direction_cosines, area, young_modulus)
        self.local_material_stiffness_matrices = self._compute_local_material_stiffness_matrices(
            self.elements.free_length,
            self.elements.direction_cosines,
            self.elements.area,
            self.elements.young
        )
        
        # Compute local geometric stiffness matrices using force densities (current tension / current length)
        force_densities = self.elements.result.tension / self.elements.length
        self.local_geometric_stiffness_matrices = self._compute_local_geometric_stiffness_matrices(force_densities)


    def _compute_local_material_stiffness_matrices(self, length: np.ndarray, cosinus: np.ndarray, 
                                                 area: np.ndarray, young: np.ndarray) -> list:
        """Compute local material stiffness matrices for each element.
        
        Args:
            length: [m] - shape (elements_count,) - (free or current) length of each element
            cosinus: [-] - shape (elements_count, 3) - Direction cosines of each element
            area: [mm²] - shape (elements_count,) - Cross-sectional area of each element
            young: [MPa] - shape (elements_count,) - Young's modulus of each element
            
        Returns:
            List of local material stiffness matrices, each of shape (6,6)
        """
        if self.elements.count == 0:
            return []
            
        # Compute element flexibilities (L/EA)
        if length == self.free_length: 
            flexibility = self.flexibility # flexibility has already been computed in super()__init__ method
        else: # user may want to compute the flexibility based on the current length rather than its free length.
            flexibility = self._compute_flexibility(young, area, length) 
        
        km_loc_list = []
        
        for i in range(self.count):
            cx, cy, cz = cosinus[i]
            cos = np.array([[-cx, -cy, -cz, cx, cy, cz]])
            R = cos.T @ cos  # local compatibility * local equilibrium
            km = (1/flexibility[i]) * R  # local material stiffness matrix
            km_loc_list.append(km)
            
        return km_loc_list
        
    def _compute_local_geometric_stiffness_matrices(self, force_densities: np.ndarray) -> list:
        """Compute local geometric stiffness matrices for each element.
        
        Args:
            force_densities: [N/m] - shape (elements_count,) - Force density (Tension/Length) of each element
            
        Returns:
            List of local geometric stiffness matrices, each of shape (6,6)
        """
        if self.count == 0:
            return []
            
        kg_loc_list = []
        for i in range(self.count):
            kg = force_densities[i] * np.array([
                [ 1, 0, 0,-1, 0, 0],
                [ 0, 1, 0, 0,-1, 0],
                [ 0, 0, 1, 0, 0,-1],
                [-1, 0, 0, 1, 0, 0],
                [ 0,-1, 0, 0, 1, 0],
                [ 0, 0,-1, 0, 0, 1]
            ])
            kg_loc_list.append(kg)
            
        return kg_loc_list
 
    def post_process(self, displacements: np.ndarray) -> np.ndarray:
        """Compute additional element tensions from nodal displacements. Note that tensions are not computed from EA(elastic_elongation)/free_length because,
         in linear calculation, tension must be computed in the initial geometry and not in the deformed geometry.
        
        Args:
            displacements: [m] - shape (3*nodes_count,) - additional Nodal displacements due to additional loads
        
        Returns:
            [N] - shape (elements_count,) - Element tensions
        """
        additional_tension = np.zeros(self.count)
        for i in range(self.count):
            n0, n1 = self.end_nodes[i]
            index = np.array([3*n0, 3*n0+1, 3*n0+2, 3*n1, 3*n1+1, 3*n1+2])
            d_local = displacements[index]  # Local displacements at element nodes
            
            # Tangent local stiffness matrix
            k_local = self.local_material_stiffness_matrices[i] + self.local_geometric_stiffness_matrices[i]
            
            # Local resisting forces at both element ends
            f_local = k_local @ d_local
            
            # Project forces to get tension
            cx, cy, cz = self.direction_cosines[i]
            additional_tension[i] = -(f_local[0]*cx + f_local[1]*cy + f_local[2]*cz) #axial forces
            
        return additional_tension