from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
import numpy as np


class Elements_Linear_DM(FEM_Elements):
    def __init__(self, nodes: FEM_Nodes, type=None, end_nodes=None, areas=None, youngs=None, 
                 delta_free_length=None, tension=None):
        """Initialize Elements_Linear_DM, extending FEM_Elements with stiffness matrices.
        
        Args:
            Same arguments as FEM_Elements
        """
        # Call parent class constructor
        super().__init__(nodes, type, end_nodes, areas, youngs, delta_free_length, tension)
        
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
        # Get current properties
        flexibility = self.flexibility # free_length / EA
        direction_cosines = self.direction_cosines
        
        # Compute local material stiffness matrices
        self.local_material_stiffness_matrices = self._compute_local_material_stiffness_matrices(
            flexibility,
            direction_cosines
        )
        
        # Compute local geometric stiffness matrices using force densities (tension / length)
        force_densities = self.tension / self.current_length
        self.local_geometric_stiffness_matrices = self._compute_local_geometric_stiffness_matrices(force_densities)

    def _compute_local_material_stiffness_matrices(self, flexibility: np.ndarray, cosinus: np.ndarray) -> list:
        """Compute local material stiffness matrices for each element.
        
        Args:
            flexibility: [m/N] - shape (elements_count,) - Element flexibilities L/(EA) based on free_length
            cosinus: [-] - shape (elements_count, 3) - Direction cosines of each element
            
        Returns:
            List of local material stiffness matrices, each of shape (6,6)
        """
        if self.count == 0:
            return []
        
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
 
    def post_process(self, displacements_increment: np.ndarray) -> np.ndarray:
        """Compute additional element tensions from nodal displacements. Note that tensions are not computed from EA(elastic_elongation)/free_length because,
         in linear calculation, tension must be computed in the initial geometry and not in the deformed geometry.
        
        Args:
            displacements_increment: [m] - shape (3*nodes_count,) - Nodal displacements due to additional loads
        
        Returns:
            [N] - shape (elements_count,) - Element tensions
        """
        tension_increment = np.zeros(self.count)
        resisting_forces_increment = np.zeros_like(displacements_increment)
        for i in range(self.count):
            n0, n1 = self.end_nodes[i]
            index = np.array([3*n0, 3*n0+1, 3*n0+2, 3*n1, 3*n1+1, 3*n1+2])
            d_local = displacements_increment[index]  # Local displacements at element nodes
            
            # Tangent local stiffness matrix
            k_local = self.local_material_stiffness_matrices[i] + self.local_geometric_stiffness_matrices[i]
            
            # Local resisting forces at both element ends
            f_local = k_local @ d_local
            resisting_forces_increment[index] += f_local
            
            # Project forces to get tension
            cx, cy, cz = self.direction_cosines[i]
            tension_increment[i] = -(float(f_local[0])*cx + float(f_local[1])*cy + float(f_local[2])*cz) #axial forces
            
        return (tension_increment, resisting_forces_increment)

    def copy(self, nodes: FEM_Nodes) -> 'Elements_Linear_DM':
        """Create a copy of this instance with the current state.
        
        Args:
            nodes: FEM_Nodes instance to reference in the copy
            
        Returns:
            A new Elements_Linear_DM instance with the current state
        """
        return Elements_Linear_DM(
            nodes=nodes,
            type=self._type.copy(),
            end_nodes=self._end_nodes.copy(),
            areas=self._areas.copy(),
            youngs=self._youngs.copy(),
            delta_free_length=self._delta_free_length.copy(),
            tension=self._tension.copy()
        )

    def copy_and_update(self, nodes: FEM_Nodes, delta_free_length: np.ndarray, tension: np.ndarray) -> 'Elements_Linear_DM':
        """Create a copy with updated state values."""
        return Elements_Linear_DM(
            nodes=nodes,
            type=self._type.copy(),
            end_nodes=self._end_nodes.copy(),
            areas=self._areas.copy(),
            youngs=self._youngs.copy(),
            delta_free_length=delta_free_length,
            tension=tension
        )

    def copy_and_add(self, nodes: FEM_Nodes, delta_free_length_increment: np.ndarray, 
                     tension_increment: np.ndarray) -> 'Elements_Linear_DM':
        """Create a copy with incremented state values."""
        return Elements_Linear_DM(
            nodes=nodes,
            type=self._type.copy(),
            end_nodes=self._end_nodes.copy(),
            areas=self._areas.copy(),
            youngs=self._youngs.copy(),
            delta_free_length=self._delta_free_length + delta_free_length_increment,
            tension=self._tension + tension_increment
        )