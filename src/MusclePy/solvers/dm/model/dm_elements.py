from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
import numpy as np


class DM_Elements(FEM_Elements):
    def __init__(self, nodes_or_elements, type=None, end_nodes=None, areas=None, youngs=None, 
                 delta_free_length=None, tension=None):
        """Initialize DM_Elements, extending FEM_Elements with local stiffness matrices.
        
        This constructor accepts either:
        1. A FEM_Nodes instance and all the parameters needed to construct a FEM_Elements instance
        2. An existing FEM_Elements instance to convert to a DM_Elements instance
        
        Args:
            nodes_or_elements: Either a FEM_Nodes instance or a FEM_Elements instance
            type: Element types, shape (elements_count,) - Only used if nodes_or_elements is FEM_Nodes
            end_nodes: Node indices, shape (elements_count, 2) - Only used if nodes_or_elements is FEM_Nodes
            areas: Cross-sections, shape (elements_count, 2) - Only used if nodes_or_elements is FEM_Nodes
            youngs: Young's moduli, shape (elements_count, 2) - Only used if nodes_or_elements is FEM_Nodes
            delta_free_length: variation of free Length, shape (elements_count,) - Only used if nodes_or_elements is FEM_Nodes
            tension: Axial forces, shape (elements_count,) - Only used if nodes_or_elements is FEM_Nodes
        """
        # Check if the first argument is a FEM_Elements instance
        if isinstance(nodes_or_elements, FEM_Elements):
            elements = nodes_or_elements
            # Assert that all other arguments are None when a FEM_Elements instance is passed
            assert all(arg is None for arg in [type, end_nodes, areas, youngs, delta_free_length, tension]), \
                "When passing a FEM_Elements instance, all other arguments must be None"
                
            # Call parent class constructor with the properties from the FEM_Elements instance
            super().__init__(
                elements.nodes,
                elements.type,
                elements.end_nodes,
                elements.areas,
                elements.youngs,
                elements.delta_free_length,
                elements.tension
            )
        else:
            # Assert that the first argument is a FEM_Nodes instance
            assert isinstance(nodes_or_elements, FEM_Nodes), "First argument must be either a FEM_Elements or a FEM_Nodes instance"           
            # First argument is a FEM_Nodes instance
            nodes = nodes_or_elements
            # Call parent class constructor with the provided parameters
            super().__init__(nodes, type, end_nodes, areas, youngs, delta_free_length, tension)
        
        # Initialize stiffness matrices attributes
        self._compute_stiffness_matrices()

    def _compute_stiffness_matrices(self):
        """Update all local stiffness matrices of the elements based on the current state."""
        from MusclePy.utils.matrix_calculations import compute_local_material_stiffness_matrices, compute_local_geometric_stiffness_matrices
        
        # local material stiffnesses : [N/m] - List(elements.count) of shape (6,6) matrices
        self.local_material_stiffness_matrices = compute_local_material_stiffness_matrices(
            self.direction_cosines,
            self.flexibility
        )
        
        # local geometric stiffnesses : [N/m] - List(elements.count) of shape (6,6) matrices
        self.local_geometric_stiffness_matrices = compute_local_geometric_stiffness_matrices(
            self.tension,
            self.current_length
        )

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
        
    def _create_copy(self, nodes, type, end_nodes, areas, youngs, delta_free_length, tension):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (DM_Elements or a child class)
        """
        return self.__class__(
            nodes,
            type=type,
            end_nodes=end_nodes,
            areas=areas,
            youngs=youngs,
            delta_free_length=delta_free_length,
            tension=tension
        )