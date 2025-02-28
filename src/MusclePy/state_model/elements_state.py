import numpy as np
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_elements_results import FEM_ElementsResults
from MusclePy.femodel.fem_actions import FEM_Actions
from MusclePy.state_model.nodes_state import Nodes_State


class Elements_State:
    def __init__(self, elements: FEM_Elements, current_nodes: Nodes_State, 
                 current_action: FEM_Actions = None, current_results: FEM_ElementsResults = None):
        """Initialize Elements_State instance to track element properties and state.
        
        Args:
            elements: FEM_Elements instance containing element properties (type, end_nodes, areas, young_moduli)
            current_nodes: Nodes_State instance containing current nodes coordinates 
            current_action: Optional FEM_Actions instance containing the current prestress (= delta_free_lengths) applied on the elements. If None, creates zero array.
            current_results: Optional FEM_ElementsResults instance containing the current tensions and elastic_elongations computed in a previous solver's step. If None, creates zero arrays.
        """
        # Validate inputs
        if not isinstance(elements, FEM_Elements):
            raise TypeError("elements must be a FEM_Elements instance")
        if not isinstance(current_nodes, Nodes_State):
            raise TypeError("nodes_state must be a Nodes_State instance")
            
        # Store private references to input objects
        self._nodes = current_nodes

        #NOTE: "self." could be replaced by "current.elements."  - although some attributes (like count, type, end_nodes, connectivity, initial_free_length) are invariable from one state to another.

        # Initialize empty attributes
        self.count = elements.count
        self.type = np.array([], dtype=int) # [-] - shape (elements.count, ) - Type of the Elements : -1 for struts, 1 for cables
        self.end_nodes = np.array([], dtype=int).reshape((0, 2)) # [-] - shape (elements.count, 2) - End nodes indices of the elements
        self.connectivity = np.array([], dtype=int) # [-] - shape (elements.count, nodes.count) - Connectivity matrix between elements and nodes
        
        self.initial_free_length = np.array([], dtype=float) # [m] - shape (elements.count, ) - Free Length of the elements in the unprestressed state
        self.delta_free_length = np.array([], dtype=float) # [m] - shape (elements.count, ) - Change in free length due to prestress
        self.free_length = np.array([], dtype=float) # [m] - shape (elements.count, ) - Current free length of the elements
        self.length = np.array([], dtype=float) # [m] - shape (elements.count, ) - Current length of the elements ( = free length + elastic elongation)
        self.direction_cosines = np.array([], dtype=float) # [-] - shape (elements.count, 3) - Direction cosines of the elements in the X, Y, Z directions

        self.result = None # FEM_ElementsResults instance containing the current Tension [N] and elastic elongation [m] of the elements
        self.area = np.array([], dtype=float) # [mm²] - shape (elements.count, ) - Area of the elements given the current tension result (considering slack cables)
        self.young = np.array([], dtype=float) # [MPa] - shape (elements.count, ) - Young Modulus of the elements given the current tension result
        self.flexibility = np.array([], dtype=float) # [mm] - shape (elements.count, ) - Flexibility of the elements

        # Initialize all attributes with proper validation and computation
        self._initialize(elements, current_nodes, current_action, current_results)
        
    def _initialize(self, elements: FEM_Elements, current_nodes: Nodes_State, 
                    current_action: FEM_Actions = None, current_results: FEM_ElementsResults = None):
        """Initialize all attributes with proper validation and computation."""

        ### STORE ###
        # Store element type
        if elements.type.size > 0:
            self.type = elements.type
            assert self.type.shape == (self.count,), f"type should have shape ({self.count},) but got {self.type.shape}"
            
        # Store end nodes and validate
        if elements.end_nodes.size > 0:
            self.end_nodes = elements.end_nodes
            assert self.end_nodes.shape == (self.count, 2), f"end_nodes should have shape ({self.count}, 2) but got {self.end_nodes.shape}"
            
        # Create connectivity matrix
        self.connectivity = self._create_connectivity_matrix(current_nodes.count, self.count, self.end_nodes)
        
        # Store current_action.delta_free_lengths
        if current_action is not None:
            assert isinstance(current_action, FEM_Actions), "current_action must be a FEM_Actions instance"
            self.delta_free_length = current_action.delta_free_lengths
            assert self.delta_free_length.shape == (self.count,), f"delta_free_lengths should have shape ({self.count},) but got {self.delta_free_length.shape}"
        else: # Initialize with zeros if no action is given
            self.delta_free_length = FEM_Actions(b=self.count).delta_free_lengths 
        
        # Store current_results
        if current_results is not None:
            assert isinstance(current_results, FEM_ElementsResults), "current_results must be a FEM_ElementsResults instance"
            self.result = current_results
            assert self.result.tension.shape == (self.count,), f"current tension should have shape ({self.count},) but got {self.result.tension.shape}"
        else: # Initialize with zeros if no results are given
            self.result = FEM_ElementsResults(b=self.count)
        
        ### COMPUTE ###
        # Compute element lengths
        self.initial_free_length = self._compute_lengths(current_nodes.initial_coordinates)
        self.free_length = self.initial_free_length + self.delta_free_length
        self.length = self._compute_lengths(current_nodes.coordinates)
        
        # Compute direction cosines
        self.direction_cosines = self._compute_direction_cosines(current_nodes.coordinates)
        
        # Compute current element properties
        self.area = self._get_current_property(self.result.tension, elements.areas, self.type)
        self.young = self._get_current_property(self.result.tension, elements.young_moduli, self.type)
        self.flexibility = self._compute_flexibility(self.young, self.area, self.free_length)

    def _create_connectivity_matrix(self, nodes_count: int, elements_count: int, end_nodes: np.ndarray) -> np.ndarray:
        """Create connectivity matrix between nodes and elements.
        
        Args:
            nodes_count: Number of nodes in the model
            elements_count: Number of elements in the model
            end_nodes: Array of shape (elements_count, 2) containing indices of element end nodes
            
        Returns:
            Array of shape (elements_count, nodes_count) where entry (i,j) is -1 if node j is the starting node of element i, 1 if node j is the ending node and 0 otherwise.
        """
        if elements_count == 0 or nodes_count == 0:
            return np.array([], dtype=int).reshape((nodes_count, 0))
            
        connectivity = np.zeros((elements_count, nodes_count), dtype=int)
        #Calculation according to references
        # Vassart, Motro, 1999, Multiparametered Formfinding Method: Application to Tensegrity Systems
        # Sheck, 1974, The force density method for formfinding and computation of networks
        for element_index, (node0, node1) in enumerate(end_nodes):
            connectivity[element_index, node0] = 1
            connectivity[element_index, node1] = -1
        
        return -connectivity #minus signe because it makes more sense to do n1-n0 (than n0-n1) when computing a cosinus (X1-X0)/Length.

    def _compute_lengths(self, coordinates: np.ndarray) -> np.ndarray:
        """Compute the length of each element given its end nodes' coordinates.
        
        Args:
            coordinates: Array of shape (nodes_count, 3) containing node coordinates
            
        Returns:
            Array of shape (elements_count,) containing element lengths
        """
        if self.count == 0:
            return np.array([], dtype=float)
            
        assert coordinates.shape == (self._nodes.count, 3), f"coordinates should have shape ({self._nodes.count}, 3) but got {coordinates.shape}"
        
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
            
        assert coordinates.shape == (self._nodes.count, 3), f"coordinates should have shape ({self._nodes.count}, 3) but got {coordinates.shape}"
        
        node0_coords = coordinates[self.end_nodes[:, 0]]
        node1_coords = coordinates[self.end_nodes[:, 1]]
        vectors = node1_coords - node0_coords
        lengths = np.linalg.norm(vectors, axis=1)
        
        # Check for zero-length elements
        if np.any(lengths == 0):
            zero_length_indices = np.where(lengths == 0)[0]
            raise ValueError(f"Zero-length elements detected at indices: {zero_length_indices}")
            
        # Compute direction cosines
        cosines = vectors / lengths[:, np.newaxis]
        return cosines

    def _get_current_property(self, tension_value: np.ndarray, property_in_compression_tension: np.ndarray, element_types: np.ndarray) -> np.ndarray:
        """Get element properties (areas or young moduli) based on tension state (compression/tension).
        
        Args:
            tension_value: Array of shape (elements_count,) containing element tensions
            property_in_compression_tension: Array of shape (elements_count, 2) containing property values for compression and tension
            element_types: Array of shape (elements_count,) containing element types
            
        Returns:
            Array of shape (elements_count,) containing current property values
        """
        if self.count == 0:
            return np.array([], dtype=float)
            
        assert tension_value.shape == (self.count,), f"tension_value should have shape ({self.count},) but got {tension_value.shape}"
        assert property_in_compression_tension.shape == (self.count, 2), f"property_in_compression_tension should have shape ({self.count}, 2) but got {property_in_compression_tension.shape}"
        assert element_types.shape == (self.count,), f"element_types should have shape ({self.count},) but got {element_types.shape}"
        
        # Get property based on tension state
        property_values = np.where(tension_value > 0,
                                 property_in_compression_tension[:, 1],  # Tension
                                 property_in_compression_tension[:, 0])  # Compression
        
        # For zero tension, use element type
        zero_tension_mask = tension_value == 0
        if np.any(zero_tension_mask):
            types = element_types[zero_tension_mask]
            property_values[zero_tension_mask] = np.where(types > 0,
                                                        property_in_compression_tension[zero_tension_mask, 1],  # Cables
                                                        property_in_compression_tension[zero_tension_mask, 0])  # Struts
        return property_values

    def _compute_flexibility(self, young_modulus: np.ndarray, area: np.ndarray, length: np.ndarray) -> np.ndarray:
        """Compute elements flexibility (L/EA).
        
        Args:
            young_modulus: Array of shape (elements_count,) containing the current Young's modulus of each element
            area: Array of shape (elements_count,) containing the current cross-sectional area of each element
            length: Array of shape (elements_count,) containing elements length
            
        Returns:
            Array of shape (elements_count,) containing elements flexibility
        """
        if self.count == 0:
            return np.array([], dtype=float)
            
        assert young_modulus.shape == (self.count,), f"young_moduli should have shape ({self.count},) but got {young_modulus.shape}"
        assert area.shape == (self.count,), f"areas should have shape ({self.count},) but got {area.shape}"
        assert length.shape == (self.count,), f"lengths should have shape ({self.count},) but got {length.shape}"
        
        # Avoid division by zero
        ea = young_modulus * area
        mask = ea > 0 # if ea is zero, flexibility L/EA is infinite
        result = np.full_like(length, 1e9)  # Initialize with 1e9 m/N for quasi infinite flexibility (e.g. slacked cables)
        result[mask] = length[mask] / ea[mask] # Calculate flexibility L/EA of bars and non-slacked cables
        return result