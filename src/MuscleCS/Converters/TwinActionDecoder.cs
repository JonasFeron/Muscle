using MuscleCore.TwinModel;
using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public class TwinActionDecoder : IPyObjectDecoder
    {
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(TwinActions))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "Twin_Actions";
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
            if (typeof(T) != typeof(TwinActions))
                return false;

            using (Py.GIL())
            {
                try
                {
                    dynamic py = pyObj.As<dynamic>();
                    
                    // Convert numpy arrays to C# arrays
                    var loads = ToCSArray2D(py.loads);
                    var deltaFreeLengths = ((PyObject)py.delta_free_lengths).As<double[]>();

                    value = (T)(object)new TwinActions(loads, deltaFreeLengths);
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in TryDecode: {ex.Message}");
                    return false;
                }
            }
        }

        private static double[,] ToCSArray2D(dynamic npArray)
        {
            // Get array dimensions
            var shape = ((PyObject)npArray.shape).As<int[]>();
            if (shape.Length != 2)
            {
                throw new ArgumentException("Expected 2D numpy array");
            }

            // Get the numpy array data directly as a contiguous array
            var flatData = ((PyObject)npArray.ravel()).As<double[]>();
            
            // Create the 2D array with the correct dimensions
            var matrix = new double[shape[0], shape[1]];
            
            // Copy the data directly into the 2D array
            Buffer.BlockCopy(flatData, 0, matrix, 0, flatData.Length * sizeof(double));
            
            return matrix;
        }
    }
}
