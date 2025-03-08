class DRconfig:
    """
    Configuration parameters for the Dynamic Relaxation method.
    
    This class contains all the parameters needed to control the behavior of the
    Dynamic Relaxation algorithm, including time step, mass parameters, and
    termination criteria.
    """
    
    def __init__(self, dt=0.01, mass_ampl_factor=1, min_mass=0.005, max_time_step=10000, max_ke_reset=1000, zero_residual_rtol=1e-6):
        """
        Initialize the Dynamic Relaxation configuration.
        
        Args:
            dt: [s] - Time step for the time incremental method
            mass_ampl_factor: Amplification factor for the fictitious masses
            min_mass: [kg] - Minimum mass applied to each DOF if null stiffness is detected
            max_time_step: Maximum number of time steps before termination
            max_ke_reset: Maximum number of kinetic energy resets before termination
            zero_residual_rtol: Threshold below which the residual magnitude is considered zero, meaning the structure is in equilibrium.
                                The tolerance is relative to the loads magnitude.
        """
        # Mass parameters
        self.mass_ampl_factor = mass_ampl_factor if mass_ampl_factor > 0 else 1  # Amplification factor for masses
        self.min_mass = min_mass if min_mass > 0 else 0.005  # [kg] - Minimum mass for each DOF
        self.huge_mass = 1e15  # [kg] - Mass applied to fixed DOFs
        
        # Time step parameters
        self.dt = dt if dt > 0 else 0.01  # [s] - Time step
        
        # Termination criteria
        self.max_time_step = max_time_step if max_time_step > 0 else 10000  # Maximum number of time steps
        self.max_ke_reset = max_ke_reset if max_ke_reset > 0 else 1000  # Maximum number of kinetic energy resets
        self.zero_residual_rtol = zero_residual_rtol if zero_residual_rtol > 0 else 1e-6  #  Tolerance for zero checks

        # Initialize counters, to be returned to the user for information regarding the solver performances.
        self.n_time_step = 0  # Number of time steps performed
        self.n_ke_reset = 0  # Number of kinetic energy resets performed