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

using Rhino.Geometry;
using System;
using System.Collections.Generic;
using MuscleCore.Solvers;
using MuscleApp.ViewModel;
using static MuscleApp.Converters.Vector3dDecoder;

namespace MuscleApp.Solvers
{
    /// <summary>
    /// Application-level representation of SVD results, using composition to wrap the core SVDResults class
    /// with additional functionality for visualization and analysis in Rhino/Grasshopper.
    /// </summary>
    public class ResultsSVD
    {
        /// <summary>
        /// The underlying core SVD results
        /// </summary>
        private readonly CoreResultsSVD _coreResults;

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
        public ResultsSVD()
        {
            _coreResults = new CoreResultsSVD();
            Ur_T = new Vector3d[0, 0];
            Um_T = new Vector3d[0, 0];
        }

        /// <summary>
        /// Initialize a ResultsSVD object that stores the results of the Singular Value Decomposition
        /// </summary>
        /// <param name="coreResults">Core SVDResults object</param>
        public ResultsSVD(CoreResultsSVD? coreResults)
        {
            if (coreResults == null)
            {
                _coreResults = new CoreResultsSVD();
                Ur_T = new Vector3d[0, 0];
                Um_T = new Vector3d[0, 0];
                return;
            }
            _coreResults = coreResults;
            
            // Convert Ur_T to Vector3d[,]
            Ur_T = ToVectors3d(coreResults.Ur_T);
            
            // Convert Um_T to Vector3d[,]
            Um_T = ToVectors3d(coreResults.Um_T);
        }
    }
}
