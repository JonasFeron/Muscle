using Rhino.Geometry;
using System;
using System.Collections.Generic;
using MuscleCore.Solvers;
using MuscleApp.ViewModel;
using static MuscleApp.Converters.Vector3dDecoder;

namespace MuscleApp.Solvers
{
    /// <summary>
    /// Application-level representation of dynamic modal analysis results, using composition to wrap the core CoreResultsDynamic class
    /// with additional functionality for visualization and analysis in Rhino/Grasshopper.
    /// </summary>
    public class ResultsDynamic
    {
        /// <summary>
        /// The underlying core Dynamic results
        /// </summary>
        private readonly CoreResultsDynamic _coreResults;

        /// <summary>
        /// Natural frequencies of the structure in Hz
        /// </summary>
        public double[] Frequencies => _coreResults.Frequencies;


        /// <summary>
        /// Number of computed modes
        /// </summary>
        public int ModeCount => _coreResults.ModeCount;

        /// <summary>
        /// Mode shapes corresponding to the natural frequencies
        /// First dimension: mode index
        /// Second dimension: node index (3 DOFs per node)
        /// </summary>
        public Vector3d[,] ModeShapes { get; private set; }

        /// <summary>
        /// A vector of masses representing a simplified version of the mass matrix for visualization purposes.
        /// Each Vector3d represents the mass in X, Y, Z directions at a node.
        /// </summary>
        public Vector3d[] Masses { get; private set; }

        /// <summary>
        /// Empty constructor for deserialization
        /// </summary>
        public ResultsDynamic()
        {
            _coreResults = new CoreResultsDynamic();
            ModeShapes = new Vector3d[0, 0];
            Masses = new Vector3d[0];
        }

        /// <summary>
        /// Initialize a ResultsDynamic object that stores the results of dynamic modal analysis
        /// </summary>
        /// <param name="coreResults">Core CoreResultsDynamic object</param>
        public ResultsDynamic(CoreResultsDynamic? coreResults)
        {
            if (coreResults == null)
            {
                _coreResults = new CoreResultsDynamic();
                ModeShapes = new Vector3d[0, 0];
                Masses = new Vector3d[0];
                return;
            }
            _coreResults = coreResults;
            
            // Convert ModeShapes to Vector3d[,]
            ModeShapes = ToVectors3d(coreResults.ModeShapes);
            
            // Convert Masses to Vector3d[]
            Masses = ToArrayVector3d(coreResults.Masses);
        }
    }
}
