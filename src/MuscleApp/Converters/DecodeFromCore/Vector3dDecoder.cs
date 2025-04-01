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

using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Rhino.Geometry;

namespace MuscleApp.Converters
{
    public static class Vector3dDecoder
    {
        /// <summary>
        /// Converts a matrix of mode vectors to a 2D array of Vector3d.
        /// </summary>
        /// <param name="modes">Matrix of mode vectors with shape (numModes, 3*nodesCount)</param>
        /// <returns>2D array of Vector3d with shape (numModes, nodesCount)</returns>
        public static Vector3d[,] ToVectors3d(double[,] modes)
        {
            // Get dimensions of the modes matrix
            int numModes = modes.GetLength(0);
            int totalDofs = modes.GetLength(1);

            // Calculate number of nodes (assuming 3 DOFs per node: X, Y, Z)
            int nodesCount = totalDofs / 3;

            // Create 2D array to store the converted modes
            Vector3d[,] modeVectors = new Vector3d[numModes, nodesCount];

            // For each mode and each node, create a Vector3d from the x, y, z components
            for (int modeIdx = 0; modeIdx < numModes; modeIdx++)
            {
                for (int nodeIdx = 0; nodeIdx < nodesCount; nodeIdx++)
                {
                    // Create a Vector3d from the x, y, z components
                    modeVectors[modeIdx, nodeIdx] = new Vector3d(
                        modes[modeIdx, 3 * nodeIdx],     // X component
                        modes[modeIdx, 3 * nodeIdx + 1], // Y component
                        modes[modeIdx, 3 * nodeIdx + 2]  // Z component
                    );
                }
            }

            return modeVectors;
        }
                /// <summary>
        /// Converts a matrix of mode vectors to a 2D array of Vector3d.
        /// </summary>
        /// <param name="input">Matrix of mode vectors with shape (numModes, 3*nodesCount)</param>
        /// <returns>2D array of Vector3d with shape (numModes, nodesCount)</returns>
        public static Vector3d[] ToArrayVector3d(double[] input)
        {
            // Get dimensions of the modes matrix
            int nodesCount = input.GetLength(0)/3;
            
            // Create 1D array to store the converted modes
            Vector3d[] result = new Vector3d[nodesCount];

            for (int nodeIdx = 0; nodeIdx < nodesCount; nodeIdx++)
            {
                    // Create a Vector3d from the x, y, z components
                    result[nodeIdx] = new Vector3d(
                        input[3 * nodeIdx],     // X component
                        input[3 * nodeIdx + 1], // Y component
                        input[3 * nodeIdx + 2]  // Z component
                    );
            }
            return result;
        }
    }
}
