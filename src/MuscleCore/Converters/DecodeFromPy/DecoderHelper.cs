// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

// PythonNETGrasshopperTemplate

// Copyright <2025> <Jonas Feron>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public static class DecoderHelper
    {
        /// <summary>
        /// Convert a numpy array to a C# 2D double array using nested loops
        /// </summary>
        public static double[,] As2dArray(dynamic npArray)
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
        /// Convert a numpy array to a C# 2D integer array
        /// </summary>
        public static int[,] AsInt2dArray(dynamic npArray)
        {
            var shape = ((PyObject)npArray.shape).As<int[]>();
            int rows = shape[0];
            int cols = shape[1];

            var result = new int[rows, cols];
            var list = npArray.tolist();
            for (int i = 0; i < rows; i++)
            {
                var row = ((PyObject)list[i]).As<int[]>();
                for (int j = 0; j < cols; j++)
                    result[i, j] = row[j];
            }

            return result;
        }

        /// <summary>
        /// Convert a numpy array to a C# 2D boolean array using nested loops
        /// </summary>
        public static bool[,] AsBool2dArray(dynamic npArray)
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
