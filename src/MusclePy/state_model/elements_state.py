import numpy as np
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_elements_results import FEM_ElementsResults
from MusclePy.femodel.fem_actions import FEM_Actions
from MusclePy.state_model.nodes_state import Nodes_State


class Elements_State:
    def __init__(self, elements: FEM_Elements, nodes_state: Nodes_State, 
                 applied_action: FEM_Actions = None, initial_results: FEM_ElementsResults = None):
        """Initialize Elements_State instance to track element properties and state.
        
        Args:
            elements: FEM_Elements instance containing element properties (type, end_nodes, areas, young_moduli)
            nodes_state: Nodes_State instance containing node coordinates and their state
            applied_action: Optional FEM_Actions instance containing delta_free_lengths. If None, creates zero array.
            initial_results: Optional FEM_ElementsResults instance with initial tensions and elastic_elongations. If None, creates zero arrays.
        """
        # Validate inputs
        if not isinstance(elements, FEM_Elements):
            raise TypeError("elements must be a FEM_Elements instance")
        if not isinstance(nodes_state, Nodes_State):
            raise TypeError("nodes_state must be a Nodes_State instance")
        
        # Initialize attributes
        self.count = elements.count
        self.nodes_count = nodes_state.count
        
        # Store element properties with validation
        if elements.type.size > 0:
            self.type = elements.type.copy()
            assert self.type.shape == (self.count,), f"type should have shape ({self.count},) but got {self.type.shape}"
        else:
            self.type = np.array([], dtype=int)
            
        if elements.end_nodes.size > 0:
            self.end_nodes = elements.end_nodes.copy()
            assert self.end_nodes.shape == (self.count, 2), f"end_nodes should have shape ({self.count}, 2) but got {self.end_nodes.shape}"
            assert np.all(self.end_nodes >= 0) and np.all(self.end_nodes < self.nodes_count), "end_nodes indices must be within valid node range"
        else:
            self.end_nodes = np.array([], dtype=int).reshape((0, 2))
        
        # Create connectivity matrix
        self.connectivity = self._create_connectivity_matrix(self.nodes_count, self.count, self.end_nodes)
        
        # Store applied action data
        if applied_action is not None:
            assert isinstance(applied_action, FEM_Actions), "applied_action must be a FEM_Actions instance"
            self.delta_free_lengths = applied_action.delta_free_lengths
            assert self.delta_free_lengths.shape == (self.count,), f"delta_free_lengths should have shape ({self.count},) but got {self.delta_free_lengths.shape}"
        else:
            self.delta_free_lengths = FEM_Actions(b=self.count).delta_free_lengths
        
        # Store initial results
        if initial_results is not None:
            assert isinstance(initial_results, FEM_ElementsResults), "initial_results must be a FEM_ElementsResults instance"
            self.initial = initial_results
            assert self.initial.tension.shape == (self.count,), f"initial tension should have shape ({self.count},) but got {self.initial.tension.shape}"
        else:
            self.initial = FEM_ElementsResults(b=self.count)
        
        # Compute lengths
        self.initial_free_lengths = self._compute_lengths(nodes_state.initial_coordinates)
        self.free_lengths = self.initial_free_lengths + self.delta_free_lengths
        self.lengths = self._compute_lengths(nodes_state.coordinates)
        
        # Compute direction cosines
        self.direction_cosines = self._compute_direction_cosines(nodes_state.coordinates)
        
        # Store element properties
        self.areas = self._get_current_property(self.initial.tension, elements.areas)
        self.young_moduli = self._get_current_property(self.initial.tension, elements.young_moduli)
        self.flexibilities = self._compute_flexibility(self.young_moduli, self.areas, self.free_lengths)

    def _create_connectivity_matrix(self, nodes_count: int, elements_count: int, end_nodes: np.ndarray) -> np.ndarray:
        """Create connectivity matrix between nodes and elements.
        
        Args:
            nodes_count: Number of nodes in the model
            elements_count: Number of elements in the model
            end_nodes: Array of shape (elements_count, 2) containing indices of element end nodes
            
        Returns:
            Array of shape (nodes_count, elements_count) where entry (i,j) is 1 if node i belongs to element j
        """
        if elements_count == 0 or nodes_count == 0:
            return np.array([], dtype=int).reshape((nodes_count, 0))
            
        connectivity = np.zeros((nodes_count, elements_count), dtype=int)
        for i, (node0, node1) in enumerate(end_nodes):
            connectivity[node0, i] = 1
            connectivity[node1, i] = 1
        return connectivity

    def _compute_lengths(self, coordinates: np.ndarray) -> np.ndarray:
        """Compute the length of each element given its end nodes' coordinates.
        
        Args:
            coordinates: Array of shape (nodes_count, 3) containing node coordinates
            
        Returns:
            Array of shape (elements_count,) containing element lengths
        """
        if self.count == 0:
            return np.array([], dtype=float)
            
        assert coordinates.shape == (self.nodes_count, 3), f"coordinates should have shape ({self.nodes_count}, 3) but got {coordinates.shape}"
        
        node0_coords = coordinates[self.end_nodes[:, 0]]
        node1_coords = coordinates[self.end_nodes[:, 1]]
        return np.linalg.norm(node1_coords - node0_coords, axis=1)

    def _compute_direction_cosines(self, coordinates: np.ndarray) -> np.ndarray:
        """Compute direction cosines (unit vectors) for each element.
        
        Args:
            coordinates: Array of shape (nodes_count, 3) containing node coordinates
            
        Returns:
            Array of shape (elements_count, 3) containing direction cosines
        """
        if self.count == 0:
            return np.array([], dtype=float).reshape((0, 3))
            
        assert coordinates.shape == (self.nodes_count, 3), f"coordinates should have shape ({self.nodes_count}, 3) but got {coordinates.shape}"
        
        node0_coords = coordinates[self.end_nodes[:, 0]]
        node1_coords = coordinates[self.end_nodes[:, 1]]
        vectors = node1_coords - node0_coords
        lengths = np.linalg.norm(vectors, axis=1)
        
        # Avoid division by zero for zero-length elements
        mask = lengths > 0
        result = np.zeros_like(vectors)
        result[mask] = vectors[mask] / lengths[mask, np.newaxis]
        return result

    def _get_current_property(self, tension_value: np.ndarray, property_in_compression_tension: np.ndarray) -> np.ndarray:
        """Get element properties based on tension state (compression/tension).
        
        Args:
            tension_value: Array of shape (elements_count,) containing element tensions
            property_in_compression_tension: Array of shape (elements_count, 2) containing property values for compression and tension
            
        Returns:
            Array of shape (elements_count,) containing current property values
        """
        if self.count == 0:
            return np.array([], dtype=float)
            
        assert tension_value.shape == (self.count,), f"tension_value should have shape ({self.count},) but got {tension_value.shape}"
        assert property_in_compression_tension.shape == (self.count, 2), f"property_in_compression_tension should have shape ({self.count}, 2) but got {property_in_compression_tension.shape}"
        
        # Get property based on tension state
        property_values = np.where(tension_value > 0,
                                 property_in_compression_tension[:, 1],  # Tension
                                 property_in_compression_tension[:, 0])  # Compression
        
        # For zero tension, use element type
        zero_tension_mask = tension_value == 0
        if np.any(zero_tension_mask):
            types = self.type[zero_tension_mask]
            property_values[zero_tension_mask] = np.where(types > 0,
                                                        property_in_compression_tension[zero_tension_mask, 1],  # Cables
                                                        property_in_compression_tension[zero_tension_mask, 0])  # Struts
        return property_values

    def _compute_flexibility(self, young_moduli: np.ndarray, areas: np.ndarray, lengths: np.ndarray) -> np.ndarray:
        """Compute element flexibilities (L/EA).
        
        Args:
            young_moduli: Array of shape (elements_count,) containing Young's moduli
            areas: Array of shape (elements_count,) containing cross-sectional areas
            lengths: Array of shape (elements_count,) containing element lengths
            
        Returns:
            Array of shape (elements_count,) containing flexibilities
        """
        if self.count == 0:
            return np.array([], dtype=float)
            
        assert young_moduli.shape == (self.count,), f"young_moduli should have shape ({self.count},) but got {young_moduli.shape}"
        assert areas.shape == (self.count,), f"areas should have shape ({self.count},) but got {areas.shape}"
        assert lengths.shape == (self.count,), f"lengths should have shape ({self.count},) but got {lengths.shape}"
        
        # Avoid division by zero
        ea = young_moduli * areas
        mask = ea > 0
        result = np.zeros_like(lengths)
        result[mask] = lengths[mask] / ea[mask]
        return result