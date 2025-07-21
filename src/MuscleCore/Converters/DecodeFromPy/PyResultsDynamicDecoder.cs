using MuscleCore.Solvers;
using Python.Runtime;
using static MuscleCore.Converters.DecoderHelper;

namespace MuscleCore.Converters
{
    /// <summary>
    /// Decoder for converting Python PyResultsDynamic objects to C# CoreResultsDynamic objects.
    /// </summary>
    public class PyResultsDynamicDecoder : IPyObjectDecoder
    {
        /// <summary>
        /// Determines if this decoder can decode the given Python object type to the specified target type.
        /// </summary>
        /// <param name="objectType">The Python object type</param>
        /// <param name="targetType">The target C# type</param>
        /// <returns>True if this decoder can decode the object, false otherwise</returns>
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(CoreResultsDynamic))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "PyResultsDynamic";
                }
                catch
                {
                    return false;
                }
            }
        }

        /// <summary>
        /// Attempts to decode a Python PyResultsDynamic object to a C# CoreResultsDynamic object.
        /// </summary>
        /// <typeparam name="T">The target type (must be CoreResultsDynamic)</typeparam>
        /// <param name="pyObj">The Python object to decode</param>
        /// <param name="value">The decoded value, if successful</param>
        /// <returns>True if decoding was successful, false otherwise</returns>
        public bool TryDecode<T>(PyObject pyObj, out T? value)
        {
            value = default;
            if (typeof(T) != typeof(CoreResultsDynamic))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Extract properties and convert to C# arrays
                    var frequencies = py.frequencies.tolist().As<double[]>();
                    var modeShapes = As2dArray(py.mode_shapes);
                    var masses = py.masses.tolist().As<double[]>();

                    // Create CoreResultsDynamic object with all properties
                    var dynamicResults = new CoreResultsDynamic(
                        frequencies: frequencies,
                        modeShapes: modeShapes,
                        masses: masses
                    );

                    value = (T)(object)dynamicResults;
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
