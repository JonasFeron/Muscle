# Muscle

# Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# List of the contributors to the development of Muscle: see NOTICE file.
# Description and complete License: see NOTICE file.


# Acknowledgements:
# The author wishes to express his sincere appreciation to Professor L. Rhode-Barbarigos (University of Miami) for his substantial guidance in the implementation of the Dynamic Relaxation method in 2021.

"""
References:
[1] Bel Hadj Ali N., Rhode-Barbarigos L., Smith I.F.C., "Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm", International Journal of Solids and Structures, Volume 48, Issue 5, 2011, Pages 637-647, https://doi.org/10.1016/j.ijsolstr.2010.10.029.
[2] Barnes MR., "Form Finding and Analysis of Tension Structures by Dynamic Relaxation". International Journal of Space Structures. 1999;14(2):89-104. doi:10.1260/0266351991494722
"""

from MusclePy.femodel.pytruss import PyTruss
from MusclePy.solvers.dr.py_truss_dr import PyTrussDR
from MusclePy.solvers.dr.py_config_dr import PyConfigDR
import numpy as np


def main_dynamic_relaxation(structure: PyTruss, loads_increment: np.ndarray = None, 
                                       free_length_variation: np.ndarray = None, config: PyConfigDR = None) -> PyTrussDR:
    """
    Perform the Dynamic Relaxation Method on the Structure.
    
    Args:
        structure: Initial structure state
        loads_increment: External load increments to apply
        free_length_variation: Free length variation to apply
        config: Configuration for the Dynamic Relaxation method
        
    Returns:
        PyTrussDR: The final structure state after Dynamic Relaxation
        
    Note:
        The config object is updated in-place with the number of time steps and kinetic energy resets.
    """

    assert isinstance(structure, PyTruss), "Structure must be a PyTruss instance"
    loads_increment = structure.nodes._check_and_reshape_array(loads_increment, "loads_increment")
    free_length_variation = structure.elements._check_and_reshape_array(free_length_variation, "free_length_variation")
    if config is None:
        config = PyConfigDR() #use default solver configuration
    else: 
        assert isinstance(config, PyConfigDR), "config must be a PyConfigDR instance"

    input_state = PyTrussDR(structure)
    
    current_state = input_state.copy_and_add(loads_increment, free_length_variation)

    # Compute Residuals
    current_state.compute_residuals() 
    
    #4) Enter the time-incremental method
    Prev = None

    while (config.n_time_step < config.max_time_step 
            and config.n_ke_reset < config.max_ke_reset 
            and not current_state.is_in_equilibrium(rtol=config.zero_residual_rtol, atol=config.zero_residual_atol)):
            
        # Compute Next State (Masses, Velocities, Displacements, Kinetic Energy)
        next_state = compute_next_state(current_state, config)
    
        # Set the new time: t <-- t+Dt
        config.n_time_step +=1
        current_state = next_state.copy()
        current_state.compute_residuals()
            
    return current_state


def compute_next_state(current: PyTrussDR, config: PyConfigDR):

    # retrieve parameters
    dt = config.dt

    # compute current masses  (eq 19 of ref [1])   
    current_masses = _compute_current_masses(current, config)
    # compute velocities increment
    velocities_incr = _compute_velocities_increments(current, config, current_masses)
    next_velocities = current.nodes.velocities + velocities_incr

    # compute displacements increment
    displacements_incr = dt * next_velocities
    next_displacements = current.nodes.displacements + displacements_incr

    # compute next kinetic energy
    next_kinetic_energy = compute_kinetic_energy(current_masses, next_velocities, current.nodes.dof)

    # if energy peak detected, reset velocities and adjust displacements
    displacements_correction = np.zeros_like(current.nodes.displacements)
    if next_kinetic_energy <= current.kinetic_energy: # energy peak detected
        current_masses = np.maximum(current_masses, config.min_mass) # avoid zero mass 
        displacements_correction = - 1.5 * dt * next_velocities + 0.5 * dt**2 * current.nodes.residuals/ current_masses
        next_kinetic_energy = 0
        next_velocities = np.zeros_like(current.nodes.velocities)
        config.n_ke_reset += 1

    # update displacements
    next_displacements += displacements_correction

    # create next state
    next_state = current.copy_and_update(
        velocities=next_velocities,
        displacements=next_displacements,
        kinetic_energy=next_kinetic_energy
    )
    return next_state


def _compute_current_masses(current: PyTrussDR, config: PyConfigDR) -> np.ndarray:
    
    # compute material + geometric stiffness matrices of shape: (3*NodesCount, 3*NodesCount)
    K = current.global_material_stiffness_matrix + current.global_geometric_stiffness_matrix
    
    #The diagonal of the matrix contains the sum of the stiffnesses for each elements, associated to one DoF
    diagonal_of_K = np.diag(K).reshape(current.nodes.count, 3)
    
    # compute masses  (eq 19 of ref [1]) - shape: (NodesCount, 3)
    current_masses = 2 * config.dt**2 * diagonal_of_K * config.mass_ampl_factor

    # deal with supports
    where_support = ~current.nodes.dof
    current_masses[where_support] = config.huge_mass  # Apply a huge mass where the DOF are fixed (False). Keep the calculated mass otherwise

    return current_masses

def _compute_velocities_increments(current: PyTrussDR, config: PyConfigDR, current_masses: np.ndarray) -> np.ndarray:
    """
    Compute the velocities increments: 

    :return: Dt * Residual/Mass (/2 when all current velocities are zero)
    """
    # retrieve parameters
    dt = config.dt
    min_mass = config.min_mass
    masses = current_masses
    residuals = current.nodes.residuals

    # avoid zero mass (this happens when the stiffness is null in eq 19 of ref [1])
    masses = np.maximum(masses, min_mass) 

    # compute velocity increment
    velocities_incr = dt * residuals / masses

    # Check if all velocities are zero
    # This happens at the beginning of the analysis, or when an energy peak is detected
    velocities = current.nodes.velocities
    all_velocities_near_zero = np.allclose(velocities, 0, rtol=1e-10, atol=1e-12)
    
    if all_velocities_near_zero:
        velocities_incr = velocities_incr / 2

    return velocities_incr



def compute_kinetic_energy(masses, velocities, dof) -> np.ndarray:
    where_no_support = dof
    KE_vector = masses * velocities **2
    KE = 0.5 * np.sum(KE_vector[where_no_support]) # Sum the Kinetic Energy only where there is no support
    return KE
