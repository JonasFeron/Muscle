using Rhino.Geometry;
using System;
using System.Collections.Generic;
using MuscleCore.Solvers;
using MuscleApp.ViewModel;

namespace MuscleApp.Solvers
{
    /// <summary>
    /// Application-level representation of SVD results, using composition to wrap the core SVDResults class
    /// with additional functionality for visualization and analysis in Rhino/Grasshopper.
    /// </summary>
    public class SVDResultsApp
    {
        /// <summary>
        /// The underlying core SVD results
        /// </summary>
        private readonly SVDResults _coreResults;

        /// <summary>
        /// Rank of equilibrium matrix
        /// </summary>
        public int r => _coreResults.r;

        /// <summary>
        /// Degree of static indeterminacy = number of self-stress modes
        /// </summary>
        public int s => _coreResults.s;

        /// <summary>
        /// Degree of kinematic indeterminacy = number of mechanisms
        /// </summary>
        public int m => _coreResults.m;

        /// <summary>
        /// R extensional modes (transposed): loads which can be equilibrated in the current structure OR extensional displacements
        /// (which elongate the elements) as row vectors
        /// </summary>
        public double[,] Ur_T => _coreResults.Ur_T;

        /// <summary>
        /// M inextensional modes (transposed): loads which can't be equilibrated in the current structure OR inextensional displacements 
        /// (mechanisms) as row vectors
        /// </summary>
        public double[,] Um_T => _coreResults.Um_T;

        /// <summary>
        /// R singular values of the equilibrium matrix
        /// </summary>
        public double[] Sr => _coreResults.Sr;

        /// <summary>
        /// R extensional modes (transposed): axial forces in equilibrium with extensional loads OR elongations compatible with extensional displacements
        /// as row vectors
        /// </summary>
        public double[,] Vr_T => _coreResults.Vr_T;

        /// <summary>
        /// S self-stress modes (transposed): axial forces in equilibrium without external loads OR "incompatible" elongations 
        /// (elongations that can exist without displacements) as row vectors
        /// </summary>
        public double[,] Vs_T => _coreResults.Vs_T;

        /// <summary>
        /// R extensional modes as Vector3d arrays
        /// First dimension: mode index
        /// Second dimension: node index
        /// </summary>
        public Vector3d[,] Ur_T { get; private set; }

        /// <summary>
        /// M inextensional modes (mechanisms) as Vector3d arrays
        /// First dimension: mode index
        /// Second dimension: node index
        /// </summary>
        public Vector3d[,] Um_T { get; private set; }

        /// <summary>
        /// Empty constructor for deserialization
        /// </summary>
        public SVDResultsApp()
        {
            _coreResults = new SVDResults();
            Ur_T = new Vector3d[0, 0];
            Um_T = new Vector3d[0, 0];
        }

        /// <summary>
        /// Initialize a SVDResultsApp object that stores the results of the Singular Value Decomposition
        /// </summary>
        /// <param name="coreResults">Core SVDResults object</param>
        public SVDResultsApp(SVDResults coreResults)
        {
            _coreResults = coreResults ?? throw new ArgumentNullException(nameof(coreResults));
            
            // Convert Ur_T to Vector3d[,]
            Ur_T = ConvertModesToVectors(coreResults.Ur_T);
            
            // Convert Um_T to Vector3d[,]
            Um_T = ConvertModesToVectors(coreResults.Um_T);
        }


        /// <summary>
        /// Converts a matrix of mode vectors to a 2D array of Vector3d.
        /// </summary>
        /// <param name="modes">Matrix of mode vectors with shape (numModes, 3*nodesCount)</param>
        /// <returns>2D array of Vector3d with shape (numModes, nodesCount)</returns>
        private static Vector3d[,] ConvertModesToVectors(double[,] modes)
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
