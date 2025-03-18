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
    }
}
