import numpy as np
from MusclePy.twin_model.twin_nodes import Twin_Nodes
from MusclePy.twin_model.twin_nodes_results import Twin_NodesResults


class Nodes_State:
    def __init__(self, initial_nodes: Twin_Nodes, applied_action=None, applied_nodes_results: Twin_NodesResults = None):
        """Initialize a Nodes_State instance.
        
        Args:
            nodes: Twin_Nodes instance containing initial coordinates and DOF information
            applied_action: TwinActions instance containing loads and delta free lengths
            applied_nodes_results: Twin_NodesResults instance containing displacements, residuals, and reactions
        """
        # Store input instances
        self.initial = initial_nodes
        self.applied_action = applied_action
        self.applied_nodes_results = applied_nodes_results if applied_nodes_results is not None else Twin_NodesResults()
        
        # Initialize attributes
        self.count = initial_nodes.count

        self.dof = initial_nodes.dof.copy() if initial_nodes.dof.size > 0 else np.array([], dtype=bool).reshape((0, 3))
        self.dof_free_count = np.sum(self.dof) if self.dof.size > 0 else 0  # Number of free degrees of freedom
        self.dof_fixed_count = np.sum(~self.dof) if self.dof.size > 0 else 0  # Number of fixed degrees of freedom
        
        # Current coordinates = initial coordinates + applied displacements
        if self.count > 0:
            self.coordinates = initial_nodes.coordinates.copy()
            if applied_nodes_results is not None and applied_nodes_results.displacements.size > 0:
                self.coordinates += applied_nodes_results.displacements
        else:
            self.coordinates = np.array([], dtype=float).reshape((0, 3))
            
        # Store other results from applied_nodes_results
        self.residual = applied_nodes_results.residual if applied_nodes_results is not None else np.array([], dtype=float).reshape((0, 3))
        self.reactions = applied_nodes_results.reactions if applied_nodes_results is not None else np.array([], dtype=float).reshape((0, 3))
        
