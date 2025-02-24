import numpy as np
from MusclePy.fem_model.fem_nodes import FEM_Nodes
from MusclePy.fem_model.fem_nodes_results import FEM_NodesResults
from MusclePy.femodel.fem_actions import FEM_Actions


class Nodes_State:
    def __init__(self, initial_nodes: FEM_Nodes, applied_action: FEM_Actions = None, initial_results: FEM_NodesResults = None):
        """Initialize a Nodes_State instance.
        
        Args:
            initial_nodes: FEM_Nodes instance containing initial coordinates and DOF information
            applied_action: FEM_Actions instance containing applied loads (and delta free lengths)
            initial_results: FEM_NodesResults instance containing initial displacements, residuals, and reactions
        """
        # Store initial_nodes data
        self.initial_coordinates = initial_nodes.coordinates
        self.count = initial_nodes.count

        self.dof = initial_nodes.dof
        self.dof_free_count = np.sum(self.dof) if self.dof.size > 0 else 0  # Number of free degrees of freedom
        self.dof_fixed_count = np.sum(~self.dof) if self.dof.size > 0 else 0  # Number of fixed degrees of freedom
        
        # Store applied_action data
        self.applied_loads = applied_action.loads if applied_action is not None else FEM_Actions(n=self.count).loads

        # Store initial results corresponding to already applied actions
        self.initial = initial_results if initial_results is not None else FEM_NodesResults(n=self.count)
        # contains:
        # self.initial.displacements 
        # self.initial.residual 
        # self.initial.reactions 

        # Current coordinates = initial coordinates + initial displacements
        self.coordinates = self.initial_coordinates + self.initial.displacements

            