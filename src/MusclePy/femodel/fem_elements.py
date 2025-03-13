import numpy as np
from .fem_nodes import FEM_Nodes


class FEM_Elements:
    def __init__(self, nodes: FEM_Nodes, type=None, end_nodes=None, area=None, youngs=None, 
                 free_length_variation=None, tension=None):
        """Python equivalent of C# FEM_Elements class.
        
        Properties:
        1. Read-Only (computed once):
            - nodes: FEM_Nodes instance
            - count: Number of elements
            - type: [-] Element types (-1: strut, 1: cable)
            - end_nodes: [-] Element-node connectivity indices
            - connectivity: [-] Element-node connectivity matrix
            - initial_free_length: [m] Length in unprestressed state
            - area: [mm²] Cross-section area of elements
            
        2. State-Dependent (computed from current state):
            - young: [MPa] Young's modulus based on tension state
            - flexibility: [m/N] = L/(EA), large value (1e6) if EA ≈ 0
            - current_length: [m] Based on current node coordinates
            - current_free_length: [m] = initial + delta
            - direction_cosines: [-] Unit vectors (x,y,z)
            
        3. Mutable State:
            - free_length_variation: [m] Change in free length
            - tension: [N] Axial force (positive in tension)
            
        Args:
            nodes: FEM_Nodes instance
            type: Element types, shape (elements_count,)
            end_nodes: Node indices, shape (elements_count, 2)
            area: Cross-sections, shape (elements_count,)
            youngs: Young's moduli, shape (elements_count, 2) : [E_if_compression, E_if_tension]
            free_length_variation: variation of free Length due to prestressing or form-finding, shape (elements_count,)
            tension: Axial forces, shape (elements_count,)
        """
        # Initialize immutable attributes (set once from C#)
        if not isinstance(nodes, FEM_Nodes):
            raise TypeError("nodes must be a FEM_Nodes instance")
        self._nodes = nodes
        self._count = 0

        self._type = np.array([], dtype=int)
        self._end_nodes = np.array([], dtype=int).reshape((0, 2))
        self._connectivity = np.array([], dtype=int).reshape((0, 0))  # Initialize empty connectivity matrix (computed from end_nodes)
        self._area = np.array([], dtype=float)
        self._youngs = np.array([], dtype=float).reshape((0, 2))
        self._initial_free_length = np.array([], dtype=float)
        
        # Initialize mutable state attributes
        self._free_length_variation = np.array([], dtype=float)
        self._tension = np.array([], dtype=float)
        
        # Initialize the instance
        self._initialize(type, end_nodes, area, youngs, free_length_variation, tension)



    # Private Initialization methods
    def _check_and_reshape_array(self, arr, name, shape_suffix=None) -> np.ndarray:
        """Convert input array to proper numpy array with correct shape and type.
        
        Handles these cases:
        1. None -> zeros array
        2. Shape (elements_count,) or (elements_count, N) -> converted to proper dtype (float or int)
        3. Shape (N*elements_count,) -> reshaped to (elements_count, N) if possible
        
        Args:
            arr: Array to convert
            name: Name of array for error messages and type detection
            shape_suffix: Optional second dimension (e.g. 2 for youngs/end_nodes)
        """
        if arr is None:
            shape = (self._count,) if shape_suffix is None else (self._count, shape_suffix)
            return np.zeros(shape, dtype=int if name in ["type", "end_nodes"] else float)
            
        # Convert to numpy array with correct dtype
        if not isinstance(arr, np.ndarray):  # if arr is a C# array
            result = np.array(arr, dtype=int if name in ["type", "end_nodes"] else float, copy=True)
        else:
            result = arr
            
        # Handle correct shape
        expected_shape = (self._count,) if shape_suffix is None else (self._count, shape_suffix)
        if result.shape == expected_shape:
            return result
            
        # Try to reshape if it's a flat array
        if result.size == np.prod(expected_shape):
            return result.reshape(expected_shape)
            
        raise ValueError(f"{name} cannot be reshaped to {expected_shape}, got shape {result.shape}")
    
    def _initialize(self, type, end_nodes, area, youngs, free_length_variation, tension):
        """Initialize all attributes with proper validation."""
        # Handle end_nodes first to establish count
        if end_nodes is not None:
            # Convert to numpy array if needed
            end_nodes_arr = end_nodes if isinstance(end_nodes, np.ndarray) else np.array(end_nodes, dtype=int)
            
            # Handle flat array case
            if end_nodes_arr.ndim == 1:
                if len(end_nodes_arr) % 2 == 0:
                    self._count = len(end_nodes_arr) // 2
                    self._end_nodes = end_nodes_arr.reshape(self._count, 2)
                else:
                    raise ValueError("end_nodes as flat array must have length divisible by 2")
            else: # handle 2D array
                if end_nodes_arr.shape[1] != 2:
                    raise ValueError(f"end_nodes as 2D array must have shape (n,2), got shape {end_nodes_arr.shape}")
                self._count = len(end_nodes_arr)
                self._end_nodes = end_nodes_arr
        else:
            raise ValueError("impossible to initialize FEM_Elements without end_nodes, no end_nodes provided")
        
        # Initialize immutable arrays
        self._type = self._check_and_reshape_array(type, "type")
        self._area = self._check_and_reshape_array(area, "area")
        self._youngs = self._check_and_reshape_array(youngs, "youngs", shape_suffix=2)
        
        # Compute initial free length from nodes coordinates
        self._compute_initial_free_length()
        
        # Compute connectivity matrix
        self._compute_connectivity()
        
        # Initialize mutable state arrays
        self._free_length_variation = self._check_and_reshape_array(free_length_variation, "free_length_variation")
        self._tension = self._check_and_reshape_array(tension, "tension")
    
    def _compute_initial_free_length(self):
        """Compute initial free length from nodes coordinates."""
        if self._count > 0:
            coords = self._nodes.initial_coordinates
            n0 = self._end_nodes[:, 0]
            n1 = self._end_nodes[:, 1]
            dx = coords[n1, 0] - coords[n0, 0]
            dy = coords[n1, 1] - coords[n0, 1]
            dz = coords[n1, 2] - coords[n0, 2]
            self._initial_free_length = np.sqrt(dx*dx + dy*dy + dz*dz)
    
    def _compute_connectivity(self):
        """Compute connectivity matrix between nodes and elements.
        """
        if self._count == 0 or self._nodes.count == 0:
            self._connectivity = np.array([], dtype=int).reshape((0, 0))
            return
            
        connectivity = np.zeros((self._count, self._nodes.count), dtype=int)
        # According to:
        # - Vassart, Motro, 1999, Multiparametered Formfinding Method: Application to Tensegrity Systems
        # - Sheck, 1974, The force density method for formfinding and computation of networks
        for element_index, (node0, node1) in enumerate(self._end_nodes):
            connectivity[element_index, node0] = 1 # start node of element
            connectivity[element_index, node1] = -1 # end node of element
        self._connectivity = -connectivity  # According to J.Feron: minus sign to make n1-n0 consistent with direction cosines (x1-x0)/L
    


    # READ Only properties
    @property
    def nodes(self) -> FEM_Nodes:
        """FEM_Nodes instance containing nodes data"""
        return self._nodes
        
    @property
    def count(self) -> int:
        """Number of elements"""
        return self._count

    @property
    def type(self) -> np.ndarray:
        """[-] - shape (elements_count,) - Type of elements (-1 for struts, 1 for cables)"""
        return self._type
    
    @property
    def end_nodes(self) -> np.ndarray:
        """[-] - shape (elements_count, 2) - Indices of end nodes"""
        return self._end_nodes
    
    @property
    def connectivity(self) -> np.ndarray:
        """[-] - shape (elements_count, nodes.count) - Connectivity matrix between elements and nodes.
        Entry (i,j) is:
        - -1 if node j is the starting node of element i
        - 1 if node j is the ending node of element i
        - 0 otherwise
        """
        return self._connectivity

    @property
    def initial_free_length(self) -> np.ndarray:
        """[m] - shape (elements_count,) - Free length in unprestressed state"""
        return self._initial_free_length

    @property
    def area(self) -> np.ndarray:
        """[mm²] - shape (elements_count,) - Cross-section area of elements"""
        return self._area
    
    @property
    def youngs(self) -> np.ndarray:
        """[MPa] - shape (elements_count, 2) - Young's moduli in compression and tension"""
        return self._youngs

    @property
    def free_length_variation(self) -> np.ndarray:
        """[m] - shape (elements_count,) - Change in free length due to prestress"""
        return self._free_length_variation
        
    @property
    def tension(self) -> np.ndarray:
        """[N] - shape (elements_count,) - Current tension in elements"""
        return self._tension
    
    
    # Computed properties
    @property
    def direction_cosines(self) -> np.ndarray:
        """[-] - shape (elements_count, 3) - Current direction cosines"""
        coords = self._nodes.coordinates
        n0 = self._end_nodes[:, 0]
        n1 = self._end_nodes[:, 1]
        dx = coords[n1, 0] - coords[n0, 0]
        dy = coords[n1, 1] - coords[n0, 1]
        dz = coords[n1, 2] - coords[n0, 2]
        current_length = np.sqrt(dx*dx + dy*dy + dz*dz)
        return np.column_stack((dx/current_length, dy/current_length, dz/current_length))

    @property
    def current_length(self) -> np.ndarray:
        """[m] - shape (elements_count,) - Current length of elements (based on current nodes coordinates)"""
        coords = self._nodes.coordinates
        n0 = self._end_nodes[:, 0]
        n1 = self._end_nodes[:, 1]
        dx = coords[n1, 0] - coords[n0, 0]
        dy = coords[n1, 1] - coords[n0, 1]
        dz = coords[n1, 2] - coords[n0, 2]
        return np.sqrt(dx*dx + dy*dy + dz*dz)
    
    @property
    def current_free_length(self) -> np.ndarray:
        """[m] - shape (elements_count,) - Current free length (initial + variation)"""
        return self._initial_free_length + self._free_length_variation

    @property
    def elastic_elongation(self) -> np.ndarray:
        """[m] - shape (elements_count,) - Elastic elongation of elements (tension positive)"""
        return self.current_length - self.current_free_length
    
    @property
    def young(self) -> np.ndarray:
        """[MPa] - shape (elements_count,) - Current Young's modulus depending on tension state"""
        return self._get_current_young(self.elastic_elongation, self._youngs)
    
    @property
    def flexibility(self) -> np.ndarray:
        """[m/N] - shape (elements_count,) - Current flexibility (L/EA).
        Returns a large value (1e6) when EA = 0 (e.g., for slack cables)."""
        
        infinite_flexibility = 1e6 # Default large value (in m/N) for zero EA
        if self._count == 0:
            return np.array([], dtype=float)
            
        ea = self.young * self.area  # [MPa * mm²] = [N]
        mask = ea > 0  # If EA is zero, flexibility L/EA is infinite
        result = np.full(self._count, infinite_flexibility, dtype=float)  
        result[mask] = self.current_free_length[mask] / ea[mask]
        return result

    # Note : tension is considered as an input to construct an element,
    # It is not computed from EA(elastic_elongation)/free_length because,
    # in linear calculation, the compatibility between displacements and elongations is linearized. 
    # Hence, the linear displacement method computes tension by post-processing the displacements.

    #private Methods
    def _get_current_young(self, elongation: np.ndarray, youngs: np.ndarray) -> np.ndarray:
        """Get elements young modulus based on current elongation (compression/tension), or maximum Young's modulus when elongation is zero.
        
        Args:
            elongation: [m] Array of shape (elements_count,) containing positive values for tension, negative values for compression, or zero for unknown
            youngs: [MPa] Array of shape (elements_count, 2) containing the young modulus values for the bilinear material in compression and tension
            
        Returns:
            [MPa] Array of shape (elements_count,) containing current Young's modulus
        """
        assert elongation.shape[0] == self.count, f"Elongation shape {elongation.shape} does not match elements count {self.count}"
        young_compression = youngs[:, 0]
        young_tension = youngs[:, 1]

        # Get property based on tension state
        current_young = np.where(elongation > 0,
                                 young_tension,  
                                 young_compression) 
        
        # When elongation is zero, use maximum Young's modulus, assuming the element will be stressed in its prefered direction.
        where0 = np.isclose(elongation, 0)
        if np.any(where0):
            current_young[where0] = np.maximum(young_compression[where0], young_tension[where0])
        
        return current_young
    
   
    def _create_copy(self, nodes, type, end_nodes, area, youngs, free_length_variation, tension):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Returns:
            A new instance of the appropriate class (FEM_Elements or a child class)
        """
        return self.__class__(
            nodes=nodes,
            type=type,
            end_nodes=end_nodes,
            area=area,
            youngs=youngs,
            free_length_variation=free_length_variation,
            tension=tension
        )
    
    # Public Methods
    def copy(self, nodes: 'FEM_Nodes') -> 'FEM_Elements':
        """Create a copy with current state.
        
        Args:
            nodes: FEM_Nodes instance to reference in the copy
            
        Returns:
            New instance with current state
        """
        return self._create_copy(
            nodes=nodes,
            type=self._type.copy(),
            end_nodes=self._end_nodes.copy(),
            area=self._area.copy(),
            youngs=self._youngs.copy(),
            free_length_variation=self._free_length_variation.copy(),
            tension=self._tension.copy()
        )
    
    def copy_and_update(self, nodes: 'FEM_Nodes', free_length_variation: np.ndarray = None, tension: np.ndarray = None) -> 'FEM_Elements':
        """Create a copy with updated state values, or use existing state if None.
        
        Args:
            nodes: FEM_Nodes instance
            free_length_variation: [m] - shape (elements_count,) - Change in free length
            tension: [N] - shape (elements_count,) - Axial forces
        """
        # Reshape inputs if needed
        if free_length_variation is None: free_length_variation = self._free_length_variation.copy()
        if tension is None: tension = self._tension.copy()
        
        free_length_variation = self._check_and_reshape_array(free_length_variation, "free_length_variation")
        tension = self._check_and_reshape_array(tension, "tension")
        
        return self._create_copy(
            nodes=nodes,
            type=self._type.copy(),
            end_nodes=self._end_nodes.copy(),
            area=self._area.copy(),
            youngs=self._youngs.copy(),
            free_length_variation=free_length_variation,
            tension=tension
        )
    
    def copy_and_add(self, nodes: FEM_Nodes, free_length_variation: np.ndarray = None, 
                     tension_increment: np.ndarray = None) -> 'FEM_Elements':
        """Create a copy with incremented state values.
        
        Args:
            nodes: FEM_Nodes instance to reference in the copy
            free_length_variation: [m] - size: elements.count - Free length increment to add
            tension_increment: [N] - size: elements.count - Tension increment to add
            
        Returns:
            New FEM_Elements with incremented state
        """
        # Create zero arrays if arguments are None
        free_length_variation = self._check_and_reshape_array(free_length_variation, "free_length_variation")
        tension_increment = self._check_and_reshape_array(tension_increment, "tension_increment")
            
        return self.copy_and_update(
            nodes=nodes,
            free_length_variation=self._free_length_variation + free_length_variation,
            tension=self._tension + tension_increment
        )