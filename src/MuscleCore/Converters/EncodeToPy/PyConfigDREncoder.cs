using MuscleCore.Solvers;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class PyConfigDREncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(CoreConfigDR);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var config = (CoreConfigDR)obj;
            using (Py.GIL())
            {
                dynamic musclepy = Py.Import("MusclePy");

                return musclepy.PyConfigDR(
                    dt: config.Dt,
                    mass_ampl_factor: config.MassAmplFactor,
                    min_mass: config.MinMass,
                    max_time_step: config.MaxTimeStep,
                    max_ke_reset: config.MaxKEResets,
                    zero_residual_rtol: config.ZeroResidualRTol,
                    zero_residual_atol: config.ZeroResidualATol
                );
            }
        }
    }
}
