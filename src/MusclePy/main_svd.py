from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.svd_results import SVDresults
from MusclePy.solvers.linear_dm.linear_dm import LinearDisplacementMethod
import numpy as np


def main_singular_value_decomposition(structure: FEM_Structure, ZeroTol: float) -> SVDresults:
    """Solve the linear displacement method for a structure with incremental loads and prestress (=free length changes).
        
    This function:
    1. Converts the structure to a linear DM compatible structure
    2. Computes equivalent prestress loads from free length changes
    3. Solves the linear system with combined loads
    4. Updates and returns the structure with the solution
        
    Args:
        structure: Current structure state
        loads_increment: [N] - shape (3*nodes.count,) - External load increments to apply
        free_length_increment: [m] - shape (elements.count,) - Free length increments to apply
            
    Returns:
        Updated FEM_Structure with incremented state
    """
    svd_results = LinearDisplacementMethod.apply_loads_and_prestress_increments(
            structure, 
            ZeroTol
    )
    return svd_results