using MuscleCore.Solvers;
using Python.Runtime;
using static MuscleCore.Converters.DecoderHelper;

namespace MuscleCore.Converters
{
    /// <summary>
    /// Decoder for converting Python SVDresults objects to C# SVDResults objects.
    /// </summary>
    public class SVDResultsDecoder : IPyObjectDecoder
    {
        /// <summary>
        /// Determines if this decoder can decode the given Python object type to the specified target type.
        /// </summary>
        /// <param name="objectType">The Python object type</param>
        /// <param name="targetType">The target C# type</param>
        /// <returns>True if this decoder can decode the object, false otherwise</returns>
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(SVDResults))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "SVDresults";
                }
                catch
                {
                    return false;
                }
            }
        }

        /// <summary>
        /// Attempts to decode a Python SVDresults object to a C# SVDResults object.
        /// </summary>
        /// <typeparam name="T">The target type (must be SVDResults)</typeparam>
        /// <param name="pyObj">The Python object to decode</param>
        /// <param name="value">The decoded value, if successful</param>
        /// <returns>True if decoding was successful, false otherwise</returns>
        public bool TryDecode<T>(PyObject pyObj, out T? value)
        {
            value = default;
            if (typeof(T) != typeof(SVDResults))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Extract scalar values
                    int r = (int)py.r;
                    int s = (int)py.s;
                    int m = (int)py.m;

                    // Extract matrices and convert to C# arrays
                    // Note: We're getting the transposed matrices directly from Python
                    var ur_T = As2dArray(py.Ur_T);
                    var um_T = As2dArray(py.Um_T);
                    var sr = py.Sr.tolist().As<double[]>();
                    var vr_T = As2dArray(py.Vr_T);
                    var vs_T = As2dArray(py.Vs_T);

                    // Create SVDResults object with all properties
                    var svdResults = new SVDResults(
                        r: r,
                        s: s,
                        m: m,
                        ur_T: ur_T,
                        um_T: um_T,
                        sr: sr,
                        vr_T: vr_T,
                        vs_T: vs_T
                    );

                    value = (T)(object)svdResults;
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
