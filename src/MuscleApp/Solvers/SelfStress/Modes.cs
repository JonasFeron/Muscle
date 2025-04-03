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


using MuscleApp.ViewModel;
using static MuscleApp.Converters.TrussEncoder;

namespace MuscleApp.Solvers
{
    public static class SelfStressModes
    {
        /// <summary>
        /// Try to localize self-stress modes using a recursive reduction algorithm by Sánchez R., Maurin B., Kazi-Aoual M. N., and Motro R., "Selfstress States 
        /// Identification and Localization in Modular Tensegrity Grids," Int. J. Sp. Struct., vol. 22, no. 4, pp. 215–224, Nov. 2007.
        /// </summary>
        /// <param name="structure">Current structure state</param>
        /// <param name="Vs_T">2D double array containing the self-stress modes to localize</param>
        /// <param name="atol">Tolerance for considering force values as zero</param>
        /// <returns>2D double array containing the localized modes</returns>
        public static double[,]? Localize(Truss structure, double[,] Vs_T, double atol)
        {
            return MuscleCore.Solvers.SelfStressModes.Localize(ToCore(structure), Vs_T, atol);
        }
    }
}