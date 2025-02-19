import numpy as np
from StructureObj import StructureObj
import clr

# Add reference to C# assembly
clr.AddReference('MuscleCS')
from Muscle.FEModel import FEM_Nodes, FEM_Elements, FEM_NodesResults, FEM_ElementsResults


def main(nodes, elements):
    """
    Main function to solve linear displacement problem using Python.NET
    
    Args:
        nodes (FEM_Nodes): Nodes data from C#
        elements (FEM_Elements): Elements data from C#
    
    Returns:
        FEM_NodesResults, FEM_ElementsResults: Results for nodes and elements
    """
    # Convert input data to numpy arrays for computation
    nodes_coord = np.array(nodes.NodesCoord)
    loads_init = np.array(nodes.LoadsInit)
    loads_to_apply = np.array(nodes.LoadsToApply)
    is_dof_free = np.array(nodes.IsDOFfree)
    
    elements_end_nodes = np.array(elements.ElementsEndNodes)
    elements_a = np.array(elements.ElementsA)
    elements_e = np.array(elements.ElementsE)
    tension_init = np.array(elements.TensionInit)
    
    # Create structure object and perform calculations
    struct = StructureObj()
    struct.nodes_coord = nodes_coord
    struct.loads_init = loads_init
    struct.loads_to_apply = loads_to_apply
    struct.is_dof_free = is_dof_free
    struct.elements_end_nodes = elements_end_nodes
    struct.elements_a = elements_a
    struct.elements_e = elements_e
    struct.tension_init = tension_init
    
    # Perform linear displacement analysis
    struct.linear_displacement_method()
    
    # Create results objects
    nodes_results = FEM_NodesResults()
    nodes_results.NodesCoord = struct.nodes_coord
    nodes_results.ReactionsInit = struct.reactions_init
    
    elements_results = FEM_ElementsResults()
    elements_results.Tension = struct.tension
    elements_results.IsInEquilibrium = struct.is_in_equilibrium
    
    return nodes_results, elements_results

def core(nodes, elements):
    """Wrapper function to maintain compatibility with existing code"""
    return main(nodes, elements)
