using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public static class DecoderHelper
    {
        /// <summary>
        /// Convert a numpy array to a C# 2D double array using Array.Copy for maximum efficiency
        /// </summary>
        public static double[,] ToCSArray2D(dynamic npArray)
        {
            // Get array dimensions
            var shape = ((PyObject)npArray.shape).As<int[]>();
            if (shape.Length != 2)
            {
                throw new ArgumentException("Expected 2D numpy array");
            }

            // Get the numpy array data as a flat array
            var flatData = ((PyObject)npArray.ravel()).As<double[]>();
            
            // Create the 2D array with the correct dimensions
            var matrix = new double[shape[0], shape[1]];
            
            // Copy the entire array at once
            Array.Copy(flatData, 0, matrix, 0, flatData.Length);
            
            return matrix;
        }

        /// <summary>
        /// Convert a numpy array to a C# 2D boolean array using Array.Copy for maximum efficiency
        /// </summary>
        public static bool[,] ToCSBoolArray2D(dynamic npArray)
        {
            // Get array dimensions
            var shape = ((PyObject)npArray.shape).As<int[]>();
            if (shape.Length != 2)
            {
                throw new ArgumentException("Expected 2D numpy array");
            }

            // Get the numpy array data as a flat array
            var flatData = ((PyObject)npArray.ravel()).As<bool[]>();
            
            // Create the 2D array with the correct dimensions
            var matrix = new bool[shape[0], shape[1]];
            
            // Copy the entire array at once
            Array.Copy(flatData, 0, matrix, 0, flatData.Length);
            
            return matrix;
        }
    }
}
