using Python.Runtime;
using MuscleCore.Converters;

namespace MuscleCore.Solvers
{
    /// <summary>
    /// Configuration parameters for the Dynamic Relaxation method.
    /// This class contains all the parameters needed to control the behavior of the
    /// Dynamic Relaxation algorithm, including time step, mass parameters, and
    /// termination criteria.
    /// </summary>
    public class CoreConfigDR
    {
        /// <summary>
        /// [s] - Time step for the time incremental method
        /// </summary>
        public double Dt { get; set; }

        /// <summary>
        /// Amplification factor for the fictitious masses
        /// </summary>
        public double MassAmplFactor { get; set; }

        /// <summary>
        /// [kg] - Minimum mass applied to each DOF if null stiffness is detected
        /// </summary>
        public double MinMass { get; set; }


        /// <summary>
        /// Maximum number of time steps before termination
        /// </summary>
        public int MaxTimeStep { get; set; }

        /// <summary>
        /// Maximum number of kinetic energy resets before termination
        /// </summary>
        public int MaxKEResets { get; set; }

        /// <summary>
        /// Relative tolerance for zero residual check, compared to external loads magnitude
        /// </summary>
        public double ZeroResidualRTol { get; set; }

        /// <summary>
        /// Absolute tolerance (in N) for zero residual check, when loads are near zero
        /// </summary>
        public double ZeroResidualATol { get; set; }

        /// <summary>
        /// Number of time steps performed (output parameter)
        /// </summary>
        public int NTimeStep { get; set; }

        /// <summary>
        /// Number of kinetic energy resets performed (output parameter)
        /// </summary>
        public int NKEReset { get; set; }

        /// <summary>
        /// Default constructor with recommended default values
        /// </summary>
        public CoreConfigDR()
        {
            Dt = 0.01;
            MassAmplFactor = 1.0;
            MinMass = 0.005;
            MaxTimeStep = 10000;
            MaxKEResets = 1000;
            ZeroResidualRTol = 1e-4;
            ZeroResidualATol = 1e-6;
            NTimeStep = 0;
            NKEReset = 0;
        }


        /// <summary>
        /// Full constructor with all parameters including output counters
        /// </summary>
        /// <param name="dt">[s] - Time step for the time incremental method</param>
        /// <param name="massAmplFactor">Amplification factor for the fictitious masses</param>
        /// <param name="minMass">[kg] - Minimum mass applied to each DOF if null stiffness is detected</param>
        /// <param name="maxTimeStep">Maximum number of time steps before termination</param>
        /// <param name="maxKEResets">Maximum number of kinetic energy resets before termination</param>
        /// <param name="zeroResidualRTol">Relative tolerance for zero residual check</param>
        /// <param name="zeroResidualATol">Absolute tolerance (in N) for zero residual check</param>
        /// <param name="nTimeStep">Number of time steps performed</param>
        /// <param name="nKEReset">Number of kinetic energy resets performed</param>
        public CoreConfigDR(
            double dt = 0.01,
            double massAmplFactor = 1.0,
            double minMass = 0.005,
            int maxTimeStep = 10000,
            int maxKEResets = 1000,
            double zeroResidualRTol = 1e-4,
            double zeroResidualATol = 1e-6,
            int nTimeStep = 0,
            int nKEReset = 0)
        {
            Dt = dt > 0 ? dt : 0.01;
            MassAmplFactor = massAmplFactor > 0 ? massAmplFactor : 1.0;
            MinMass = minMass > 0 ? minMass : 0.005;
            MaxTimeStep = maxTimeStep > 0 ? maxTimeStep : 10000;
            MaxKEResets = maxKEResets > 0 ? maxKEResets : 1000;
            ZeroResidualRTol = zeroResidualRTol > 0 ? zeroResidualRTol : 1e-4;
            ZeroResidualATol = zeroResidualATol > 0 ? zeroResidualATol : 1e-6;
            NTimeStep = nTimeStep;
            NKEReset = nKEReset;
        }
    }
}
