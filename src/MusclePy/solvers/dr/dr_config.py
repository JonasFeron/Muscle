class DRconfig:
    """
    Configuration parameters for the Dynamic Relaxation method.
    
    This class contains all the parameters needed to control the behavior of the
    Dynamic Relaxation algorithm, including time step, mass parameters, and
    termination criteria.
    """
    
    def __init__(self, dt=0.01, ampl_mass=1, min_mass=0.005, max_time_step=10000, max_ke_reset=1000):
        """
        Initialize the Dynamic Relaxation configuration.
        
        Args:
            dt: [s] - Time step for the time incremental method
            ampl_mass: Amplification factor for the fictitious masses
            min_mass: [kg] - Minimum mass applied to each DOF if null stiffness is detected
            max_time_step: Maximum number of time steps before termination
            max_ke_reset: Maximum number of kinetic energy resets before termination
        """
        # Mass parameters
        self.ampl_mass = ampl_mass if ampl_mass > 0 else 1  # Amplification factor for masses
        self.min_mass = min_mass if min_mass > 0 else 0.005  # [kg] - Minimum mass for each DOF
        self.huge_mass = 1e15  # [kg] - Mass applied to fixed DOFs
        
        # Time step parameters
        self.dt = dt if dt > 0 else 0.01  # [s] - Time step
        
        # Termination criteria
        self.max_time_step = max_time_step if max_time_step > 0 else 10000  # Maximum number of time steps
        self.max_ke_reset = max_ke_reset if max_ke_reset > 0 else 1000  # Maximum number of kinetic energy resets
      