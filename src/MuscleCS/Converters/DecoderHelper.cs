using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public static class DecoderHelper
    {
        /// <summary>
        /// Convert a numpy array to a C# 2D double array using efficient Buffer.BlockCopy
        /// </summary>
        public static double[,] ToCSArray2D(dynamic npArray)
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

        /// <summary>
        /// Convert a numpy array to a C# 2D boolean array using efficient Buffer.BlockCopy
        /// </summary>
        public static bool[,] ToCSBoolArray2D(dynamic npArray)
        {
            // Get array dimensions
            var shape = ((PyObject)npArray.shape).As<int[]>();
            if (shape.Length != 2)
            {
                throw new ArgumentException("Expected 2D numpy array");
            }

            // Get the numpy array data directly as a contiguous array
            var flatData = ((PyObject)npArray.ravel()).As<bool[]>();
            
            // Create the 2D array with the correct dimensions
            var matrix = new bool[shape[0], shape[1]];
            
            // Copy the data directly into the 2D array
            Buffer.BlockCopy(flatData, 0, matrix, 0, flatData.Length * sizeof(bool));
            
            return matrix;
        }
    }
}
