import numpy as np
from MusclePy.fem_model.fem_nodes import FEM_Nodes
from MusclePy.fem_model.fem_nodes_results import FEM_NodesResults
from MusclePy.femodel.fem_actions import FEM_Actions


class Nodes_State:
    def __init__(self, initial_nodes: FEM_Nodes, current_action: FEM_Actions = None, current_results: FEM_NodesResults = None):
        """Initialize a Nodes_State instance.
        
        Args:
            initial_nodes: FEM_Nodes instance containing initial coordinates and degrees of freedom
            current_action: FEM_Actions instance containing the current loads applied on the nodes. If None, creates zero array.
            current_results: FEM_NodesResults instance containing current displacements, residuals, and reactions computed in a previous solver's step. If None, creates zero arrays.
        """
        # Validate inputs
        if not isinstance(initial_nodes, FEM_Nodes):
            raise TypeError("initial_nodes must be a FEM_Nodes instance")
            
        # Initialize empty attributes
        self.count = initial_nodes.count
        self.initial_coordinates = np.array([], dtype=float).reshape((0, 3)) # [m] - shape (nodes.count, 3) - Initial coordinates of the nodes
        self.coordinates = np.array([], dtype=float).reshape((0, 3)) # [m] - shape (nodes.count, 3) - Current coordinates of the nodes
        self.dof = np.array([], dtype=bool).reshape((0, 3)) # [-] - shape (nodes.count, 3) - Degrees of freedom of the nodes (True if free, False if fixed)
        self.dof_fixed_count = 0 # [-] - Number of fixed degrees of freedom
        
        self.applied_loads = np.array([], dtype=float).reshape((0, 3)) # [N] - shape (nodes.count, 3) - Current loads applied on the nodes
        
        self.result = None # FEM_NodesResults instance containing current displacements [m], residuals [N] and reactions [N] corresponding to the current applied loads. 
        
        # Initialize all attributes with proper validation and computation
        self._initialize(initial_nodes, current_action, current_results)
        
    def _initialize(self, initial_nodes: FEM_Nodes, current_action: FEM_Actions = None, current_results: FEM_NodesResults = None):
        """Initialize all attributes with proper validation and computation."""
        
        ### STORE ###
        # Store initial coordinates and validate
        if initial_nodes.coordinates.size > 0:
            self.initial_coordinates = initial_nodes.coordinates
            assert self.initial_coordinates.shape == (self.count, 3), f"initial_coordinates should have shape ({self.count}, 3) but got {self.initial_coordinates.shape}"
            
        # Store degrees of freedom and validate
        if initial_nodes.dof.size > 0:
            self.dof = initial_nodes.dof
            assert self.dof.shape == (self.count, 3), f"dof should have shape ({self.count}, 3) but got {self.dof.shape}"
            self.dof_fixed_count = np.sum(~self.dof)
            
        # Store current_action loads
        if current_action is not None:
            assert isinstance(current_action, FEM_Actions), "current_action must be a FEM_Actions instance"
            self.applied_loads = current_action.loads
            assert self.applied_loads.shape == (self.count, 3), f"applied_loads should have shape ({self.count}, 3) but got {self.applied_loads.shape}"
        else: # Initialize with zeros if no action is given
            self.applied_loads = FEM_Actions(n=self.count).loads
            
        # Store current_results
        if current_results is not None:
            assert isinstance(current_results, FEM_NodesResults), "current_results must be a FEM_NodesResults instance"
            self.result = current_results
            assert self.result.displacements.shape == (self.count, 3), f"current displacements should have shape ({self.count}, 3) but got {self.result.displacements.shape}"
        else: # Initialize with zeros if no results are given
            self.result = FEM_NodesResults(n=self.count)
            
        ### COMPUTE ###
        # Compute current coordinates
        self.coordinates = self.initial_coordinates + self.result.displacements