//PythonNETGrasshopperTemplate

//Copyright <2025> <Jonas Feron>

//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.

//List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
//Description and complete License: see NOTICE file.

using MuscleApp.ViewModel;
using static MuscleApp.Converters.StructureStateEncoder;
using MuscleCore.Solvers; 

namespace MuscleApp.Solvers
{
    public static class SVD
    {
        /// <summary>
        /// Solve the singular value decomposition for a structure in its current state.
        /// </summary>
        /// <param name="initialStructure">Current structure state</param>
        /// <param name="rtol">Tolerance for considering singular values as zero, relative to the highest singular value</param>
        /// <returns>SVDResults object containing the SVD results</returns>
        public static SVDResults? Solve(StructureState initialStructure, double rtol)
        {
            return MuscleCore.Solvers.SVD.Solve(ToFEM(initialStructure), rtol);
        }
    }
}
