from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.solvers.nonlinear_dm.nonlinear_dm import NonlinearDisplacementMethod
import numpy as np


def main_nonlinear_displacement_method(structure: FEM_Structure, loads_increment: np.ndarray, n_steps: int) -> FEM_Structure:
    """Solve the nonlinear displacement method for a structure with incremental loads.
        
    This function:
    1. Converts the structure to a linear DM compatible structure
    2. Iteratively solves linear systems with updated geometry and stiffness
    3. Uses arc length control to ensure convergence
    4. Updates and returns the structure with the solution
        
    Args:
        structure: Current structure state
        loads_increment: [N] - shape (3*nodes.count,) - External load increments to apply
        n_steps: Number of steps to use in the nonlinear solver
            
    Returns:
        Updated FEM_Structure with incremented state
    """
    deformed_state = NonlinearDisplacementMethod.incremental_newton_raphson_procedure(
            structure, 
            loads_increment, 
            n_steps
    )
    return deformed_state
