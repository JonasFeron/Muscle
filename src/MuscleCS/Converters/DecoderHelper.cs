using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public static class DecoderHelper
    {
        /// <summary>
        /// Convert a numpy array to a C# 2D double array using nested loops
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
            
            // Copy using nested loops
            int k = 0;
            for (int i = 0; i < shape[0]; i++)
            {
                for (int j = 0; j < shape[1]; j++)
                {
                    matrix[i,j] = flatData[k++];
                }
            }
            
            return matrix;
        }

        /// <summary>
        /// Convert a numpy array to a C# 2D boolean array using nested loops
        /// </summary>
        public static bool[,] ToCSBoolArray2D(dynamic npArray)
        {
            // Get array dimensions
            var shape = ((PyObject)npArray.shape).As<int[]>();
            if (shape.Length != 2)
            {
                throw new ArgumentException("Expected 2D numpy array");
            }
            
            // Create the 2D array with the correct dimensions
            var matrix = new bool[shape[0], shape[1]];
            
            // Copy using nested loops and get values directly
            for (int i = 0; i < shape[0]; i++)
            {
                for (int j = 0; j < shape[1]; j++)
                {
                    matrix[i,j] = (bool)((PyObject)npArray.item(i, j)).As<bool>();
                }
            }
            
            return matrix;
        }
    }
}
