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

using System;

namespace MuscleCore.Solvers
{
    /// <summary>
    /// This class stores the results of the Singular Value Decomposition of the Equilibrium Matrix of the structure in the current state.
    /// Ref: S. Pellegrino, 1993, Structural computations with the singular value decomposition of the equilibrium matrix
    /// </summary>
    public class CoreResultsSVD
    {
        /// <summary>
        /// Rank of equilibrium matrix
        /// </summary>
        public int r { get; private set; }

        /// <summary>
        /// Degree of static indeterminacy = number of self-stress modes
        /// </summary>
        public int s { get; private set; }

        /// <summary>
        /// Degree of kinematic indeterminacy = number of mechanisms
        /// </summary>
        public int m { get; private set; }

        /// <summary>
        /// R extensional modes (transposed): loads which can be equilibrated in the current structure OR extensional displacements
        /// (which elongate the elements) as row vectors
        /// </summary>
        public double[,] Ur_T { get; private set; }

        /// <summary>
        /// M inextensional modes (transposed): loads which can't be equilibrated in the current structure OR inextensional displacements 
        /// (mechanisms) as row vectors
        /// </summary>
        public double[,] Um_T { get; private set; }

        /// <summary>
        /// R singular values of the equilibrium matrix
        /// </summary>
        public double[] Sr { get; private set; }

        /// <summary>
        /// R extensional modes (transposed): axial forces in equilibrium with extensional loads OR elongations compatible with extensional displacements
        /// as row vectors
        /// </summary>
        public double[,] Vr_T { get; private set; }

        /// <summary>
        /// S self-stress modes (transposed): axial forces in equilibrium without external loads OR "incompatible" elongations 
        /// (elongations that can exist without displacements) as row vectors
        /// </summary>
        public double[,] Vs_T { get; private set; }

        /// <summary>
        /// Empty constructor for deserialization
        /// </summary>
        public CoreResultsSVD()
        {
            // Initialize with empty arrays to prevent null reference exceptions
            Ur_T = new double[0, 0];
            Um_T = new double[0, 0];
            Sr = new double[0];
            Vr_T = new double[0, 0];
            Vs_T = new double[0, 0];
        }

        /// <summary>
        /// Initialize a CoreResultsSVD object that stores the results of the Singular Value Decomposition
        /// </summary>
        /// <param name="r">Rank of equilibrium matrix</param>
        /// <param name="s">Degree of static indeterminacy = number of self-stress modes</param>
        /// <param name="m">Degree of kinematic indeterminacy = number of mechanisms</param>
        /// <param name="ur_T">R extensional modes as row vectors</param>
        /// <param name="um_T">M inextensional modes as row vectors</param>
        /// <param name="sr">R singular values</param>
        /// <param name="vr_T">R extensional modes as row vectors</param>
        /// <param name="vs_T">S self-stress modes as row vectors</param>
        public CoreResultsSVD(int r, int s, int m, double[,] ur_T, double[,] um_T, double[] sr, double[,] vr_T, double[,] vs_T)
        {
            this.r = r;
            this.s = s;
            this.m = m;
            Ur_T = ur_T ?? throw new ArgumentNullException(nameof(ur_T));
            Um_T = um_T ?? throw new ArgumentNullException(nameof(um_T));
            Sr = sr ?? throw new ArgumentNullException(nameof(sr));
            Vr_T = vr_T ?? throw new ArgumentNullException(nameof(vr_T));
            Vs_T = vs_T ?? throw new ArgumentNullException(nameof(vs_T));
        }
    }
}
