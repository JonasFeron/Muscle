from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.prestress_increment import PrestressIncrement
from MusclePy.solvers.dm.linear_dm import core_linear_displacement_method, perturb
import numpy as np


def main_nonlinear_displacement_method(structure: FEM_Structure, loads_increment: np.ndarray, n_steps: int) -> FEM_Structure:
    """Execute the incremental (but not iterative) Newton-Raphson procedure with arc length control.
    
    Args:
        structure: Initial state of the linear structure
        loads_increment: Total load increment to apply
        n_steps: Number of steps to use in the nonlinear solver
        
    Returns:
        FEM_Structure in deformed state
    """
    # Note: the PrestressIncrement class does not work well with the nonlinear DM.
    # this is due to the reorientation of the elements during a non linear procedure.
    # Indeed, the loads equivalent to the prestress are not fixed once for all. Instead the prestress loads reorient with the elements
    # -> use Dynamic Relaxation for non-linear prestressing problems.

    # total loads increment to apply on the structure
    loads_increment = structure.nodes._check_and_reshape_array(loads_increment, "loads_increment")
    total_loads_incr = loads_increment.reshape((-1, ))

    # Initialize solver parameters
    l0 = 1 / n_steps  # incremental length
    max_steps = n_steps * 5  # max number of steps allowed
    perturbation = 1e-3  # [m] perturbation of the nodes coordinates if singular matrix

    # Initialize solution tracking variables
    step = 0  # current step number
    _lambda = 0.0  # advancement factor: 0 <= lambda <= 1 (lambda=1 is final stage)

    # Initialize incremental variables to be added on the structure at each step
    loads_incr = np.zeros((3 * structure.nodes.count,)) # a fraction of the total load increment
    displacements_incr = np.zeros((3 * structure.nodes.count,))
    resisting_forces_incr = np.zeros((3 * structure.nodes.count,))
    tensions_incr = np.zeros((structure.elements.count,))
    reactions_incr = np.zeros((np.sum(~structure.nodes.dof.flatten()),))
    
    previous_state = structure.copy()
    
    # Iteratively solve until convergence or max steps reached
    while (_lambda < 1 and step < max_steps):
        # update current state on which a new load_increment will be applied
        current_state = previous_state.copy_and_add(
            loads_increment=loads_incr,
            displacements_increment=displacements_incr,
            reactions_increment=reactions_incr,
            tension_increment=tensions_incr,
            resisting_forces_increment=resisting_forces_incr
            ) # note that at step 0 , the increments are 0, so the current_state is the initial_state
        
        # the current_state contains the results from the previous calculation

        try:
            # Apply the total load increment on the current state of the structure, given the current structure's stiffness
            v, r, f, t = core_linear_displacement_method(current_state, total_loads_incr) 
            # v, r, f, t are the total increments of displacements, reactions, resisting forces and axial forces, due to the application of the total load increment.
            # see Jonas Feron's master thesis (2016) for explanations.  
            
        except np.linalg.LinAlgError:
            # In case of singular matrix, perturb the structure with tiny displacements
            perturbed = perturb(current_state, magnitude=perturbation)
            current_state = perturbed.copy()
            v, r, f, t = core_linear_displacement_method(current_state, total_loads_incr)
            
        # Calculate advancement using arc length control
        d_lambda = _arc_length_control(l0, _lambda, v, total_loads_incr)
        
        # Update solution increments
        step += 1
        _lambda += d_lambda
        loads_incr = total_loads_incr * d_lambda # the current loads increment is a fraction of the total load increment
        displacements_incr = v * d_lambda
        tensions_incr = t * d_lambda
        reactions_incr = r * d_lambda
        resisting_forces_incr = f * d_lambda

        # Update previous state 
        previous_state = current_state.copy()

    # when _lambda reaches exactly 1, the while loop stops, so apply the last load increment
    final_state = previous_state.copy_and_add(
            loads_increment=loads_incr,
            displacements_increment=displacements_incr,
            reactions_increment=reactions_incr,
            tension_increment=tensions_incr,
            resisting_forces_increment=resisting_forces_incr
            )
    return final_state


def _arc_length_control(l0: float, _lambda: float, v: np.ndarray, p: np.ndarray) -> float:
    """Calculate the increment of advancement in the procedure using arc length control method.

    Args:
        l0 (float): Incremental length : l0 = 1/100 means the solver will try to reach a solution in 100 incremental steps.
        _lambda (float): Factor of advancement in the incremental procedure: 0 <= lambda <= 1 (lambda=1 corresponds to the final stage)
        v (np.ndarray): Displacement vector obtained by linear analysis when applying the total load p given the current stiffness.
        p (np.ndarray): Total loads increment to be applied on the structure

    Returns:
        float: Increment of advancement in the procedure (d_lambda)
    """
    if l0 == 1:  # if incremental length = 1
        d_lambda = 1  # final stage is obtained in one step. NonLinear Method = Linear Method
    else:  # use arclength constrain
        norm_squared = (v.T@v)
        f = np.sqrt(1 + norm_squared)  # scalar
        d_lambda = (l0 / f) * np.sign(np.dot(p.transpose(), v))  # it can be negative

    if _lambda + d_lambda > 1:  # Ensure to stop exactly on Final Stage: lambda=1.
        d_lambda = 1 - _lambda
            
    return d_lambda
