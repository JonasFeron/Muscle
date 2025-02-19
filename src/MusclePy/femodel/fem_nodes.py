import clr
import System
from System import Array
import numpy as np

# Add references to the C# assemblies
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_Nodes as CS_FEM_Nodes
from Muscle.Structure import StructureObj

class FEM_Nodes:
    def __init__(self):
        """Python equivalent of C# FEM_Nodes class"""
        # Nodes
        self.nodes_coord = np.array([], dtype=float)  # shape (NodesCount, 3)
        self.loads_init = np.array([], dtype=float)  # shape (NodesCount, 3)
        self.loads_to_apply = np.array([], dtype=float)  # shape (NodesCount, 3)

        # Supports
        self.is_dof_free = np.array([], dtype=bool)  # [bool] - shape (3NodesCount,). Each point i is associated to its X DOF (3i), Y DOF (3i+1), Z DOF (3i+2). Each DOF can be fixed (False) or free (True).
        self.reactions_init = np.array([], dtype=float)  # shape (3NodesCount,)

    def register_nodes(self, struct_obj: StructureObj):
        """Register nodes from a StructureObj"""
        node_count = len(struct_obj.StructuralNodes)
        
        # Initialize arrays with correct sizes
        self.nodes_coord = np.zeros((node_count, 3))
        self.loads_init = np.zeros((node_count, 3))
        self.loads_to_apply = np.zeros((node_count, 3))
        self.is_dof_free = np.zeros(3 * node_count, dtype=bool)
        self.reactions_init = np.zeros(3 * node_count)

        # Fill arrays with data from struct_obj
        for i in range(node_count):
            n = struct_obj.StructuralNodes[i]
            
            # Coordinates (Python works in m - C# works in m)
            self.nodes_coord[i, 0] = n.Point.X
            self.nodes_coord[i, 1] = n.Point.Y
            self.nodes_coord[i, 2] = n.Point.Z

            # DOF freedom
            self.is_dof_free[3 * i] = n.isXFree
            self.is_dof_free[3 * i + 1] = n.isYFree
            self.is_dof_free[3 * i + 2] = n.isZFree

            # Initial loads (Python works in N - C# works in N)
            self.loads_init[i, 0] = n.Load.X
            self.loads_init[i, 1] = n.Load.Y
            self.loads_init[i, 2] = n.Load.Z

            # Loads to apply
            self.loads_to_apply[i, 0] = struct_obj.LoadsToApply[n.Ind].X
            self.loads_to_apply[i, 1] = struct_obj.LoadsToApply[n.Ind].Y
            self.loads_to_apply[i, 2] = struct_obj.LoadsToApply[n.Ind].Z

            # Reactions
            if not n.isXFree:
                self.reactions_init[3 * i] = n.Reaction.X  # add the reaction if the X dof is fixed
            if not n.isYFree:
                self.reactions_init[3 * i + 1] = n.Reaction.Y
            if not n.isZFree:
                self.reactions_init[3 * i + 2] = n.Reaction.Z

    def to_cs_nodes(self) -> CS_FEM_Nodes:
        """Convert Python FEM_Nodes to C# FEM_Nodes"""
        cs_nodes = CS_FEM_Nodes()
        
        # Convert numpy arrays to C# arrays
        cs_nodes.NodesCoord = self._to_2d_array(self.nodes_coord, float)
        cs_nodes.LoadsInit = self._to_2d_array(self.loads_init, float)
        cs_nodes.LoadsToApply = self._to_2d_array(self.loads_to_apply, float)
        cs_nodes.IsDOFfree = Array[bool](self.is_dof_free)
        cs_nodes.ReactionsInit = Array[float](self.reactions_init)
        
        return cs_nodes

    @staticmethod
    def from_cs_nodes(cs_nodes: CS_FEM_Nodes):
        """Create Python FEM_Nodes from C# FEM_Nodes"""
        py_nodes = FEM_Nodes()
        
        # Convert C# arrays to numpy arrays
        py_nodes.nodes_coord = np.array(list(cs_nodes.NodesCoord)).reshape(-1, 3)
        py_nodes.loads_init = np.array(list(cs_nodes.LoadsInit)).reshape(-1, 3)
        py_nodes.loads_to_apply = np.array(list(cs_nodes.LoadsToApply)).reshape(-1, 3)
        py_nodes.is_dof_free = np.array(list(cs_nodes.IsDOFfree))
        py_nodes.reactions_init = np.array(list(cs_nodes.ReactionsInit))
        
        return py_nodes

    def _to_2d_array(self, arr: np.ndarray, dtype) -> Array[Array[dtype]]:
        """Convert numpy 2D array to C# 2D array"""
        if arr.size == 0:
            return Array[Array[dtype]]([])
        rows, cols = arr.shape
        result = Array[Array[dtype]](rows)
        for i in range(rows):
            result[i] = Array[dtype](arr[i])
        return result
