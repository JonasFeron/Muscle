using MuscleCore.Solvers;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class PyConfigDRDecoder : IPyObjectDecoder
    {
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(CoreConfigDR))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "PyConfigDR";
                }
                catch
                {
                    return false;
                }
            }
        }

        public bool TryDecode<T>(PyObject pyObj, out T? value)
        {
            value = default;
            if (typeof(T) != typeof(CoreConfigDR))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Create configuration object with all properties
                    var config = new CoreConfigDR
                    {
                        Dt = (double)py.dt,
                        MassAmplFactor = (double)py.mass_ampl_factor,
                        MinMass = (double)py.min_mass,
                        MaxTimeStep = (int)py.max_time_step,
                        MaxKEResets = (int)py.max_ke_reset,
                        ZeroResidualRTol = (double)py.zero_residual_rtol,
                        ZeroResidualATol = (double)py.zero_residual_atol,
                        NTimeStep = (int)py.n_time_step,
                        NKEReset = (int)py.n_ke_reset
                    };

                    value = (T)(object)config;
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in TryDecode: {ex.Message}\n{ex.StackTrace}");
                    return false;
                }
            }
        }
    }
}
