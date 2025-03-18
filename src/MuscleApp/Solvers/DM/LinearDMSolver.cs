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
using static MuscleApp.Converters.StructureStateDecoder;

namespace MuscleApp.Solvers
{
    public static class LinearDM
    {
        /// <summary>
        /// Solve the linear displacement method for a structure with incremental loads and prestress (free length changes).
        /// </summary>
        /// <param name="initialStructure">Current structure state</param>
        /// <param name="loadsIncrement">[N] - shape (3*nodes.count,) - External load increments to apply</param>
        /// <param name="freeLengthVariation">[m] - shape (elements.count,) - Free length increments to apply</param>
        /// <returns>Updated StructureState with incremented state</returns>
        public static StructureState? Solve(StructureState initialStructure, double[] loadsIncrement, double[] freeLengthVariation)
        {
            var femResults = MuscleCore.Solvers.LinearDM.Solve(ToCore(initialStructure), loadsIncrement, freeLengthVariation);

            var updatedStructure = CopyAndUpdate(initialStructure, femResults);

            return updatedStructure;
        }
    }
}
