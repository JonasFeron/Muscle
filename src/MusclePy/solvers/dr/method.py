from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.solvers.dr.dr_config import DRconfig
from MusclePy.solvers.dr.dr_structure import DR_Structure
import numpy as np

class DynamicRelaxation:
    @staticmethod
    def main(structure: FEM_Structure, loads_increment: np.ndarray, 
                                           free_length_increment: np.ndarray, config: DRconfig) -> DR_Structure:
        """
        Perform the Dynamic Relaxation Method on the Start State of the Structure.
        This method assumes that the StructureObject has already been initialized with InitialData method
        :return: The final State of the structure in Equilibrium
        """
          #ref:
        # [1] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm
        # [2] Barnes, 1999, Form finding and analysis of tension structures by dynamic relaxation

  

        input_state = DR_Structure(structure)
        
        current_state = input_state.copy_and_add(loads_increment, free_length_increment)

        # Compute Residuals
        current_state.compute_residuals() 

        #4) Enter the time-incremental method
        Prev = None

        while (config.n_time_step < config.max_time_step 
               and config.n_ke_reset < config.max_ke_reset 
               and current_state.is_in_equilibrium(config.zero_residual_rtol) == False):
            
            # Compute Next State (Masses, Velocities, Displacements, Kinetic Energy)
            next_state = DynamicRelaxation.compute_next_state(current_state, config)

            # Set the new time: t <-- t+Dt
            config.n_time_step +=1
            current_state = next_state.copy()
            current_state.compute_residuals()
            
        return current_state




    @staticmethod
    def compute_next_state(current: DR_Structure, config: DRconfig):

        # retrieve parameters
        dt = config.dt

        # compute current masses  (eq 19 of ref [1])   
        current_masses = DynamicRelaxation._compute_current_masses(current, config)
        # compute velocities increment
        velocities_incr = DynamicRelaxation._compute_velocities_increments(current, config, current_masses)
        next_velocities = current.nodes.velocities + velocities_incr

        # compute displacements increment
        displacements_incr = dt * next_velocities
        next_displacements = current.nodes.displacements + displacements_incr

        # compute next kinetic energy
        next_kinetic_energy = DynamicRelaxation.compute_kinetic_energy(current_masses, next_velocities, current.nodes.dof)

        # if energy peak detected, reset velocities and adjust displacements
        displacements_correction = np.zeros_like(current.nodes.displacements)
        if next_kinetic_energy <= current.kinetic_energy: # energy peak detected
            displacements_correction = - 1.5 * dt * next_velocities + 0.5 * dt**2 * current.nodes.residuals/ current.nodes.masses
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

    @staticmethod
    def _compute_current_masses(current: DR_Structure, config: DRconfig) -> np.ndarray:
        
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

    @staticmethod
    def _compute_velocities_increments(current: DR_Structure, config: DRconfig, current_masses: np.ndarray) -> np.ndarray:
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


    @staticmethod
    def compute_kinetic_energy(masses, velocities, dof) -> np.ndarray:
        where_no_support = dof
        KE_vector = masses * velocities **2
        KE = 0.5 * np.sum(KE_vector[where_no_support]) # Sum the Kinetic Energy only where there is no support
        return KE


