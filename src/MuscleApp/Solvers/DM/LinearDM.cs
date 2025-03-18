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
using MuscleCore.FEModel;
using MuscleApp.Converters;
using System.Collections.Generic;
using System.Linq;
using MuscleCore.Solvers;

namespace MuscleApp.Solvers
{
    public static class LinearDM
    {
        /// <summary>
        /// Solve the linear displacement method for a structure with incremental loads and prestress (free length changes).
        /// </summary>
        /// <param name="truss">Current structure state</param>
        /// <param name="loadsIncrement">[N] - shape (3*nodes.count,) - External load increments to apply</param>
        /// <param name="prestress">Collection of Prestress instances defining free length variations to apply</param>
        /// <returns>Updated Truss with incremented state</returns>
        public static Truss? Solve(Truss truss, double[] loadsIncrement, IEnumerable<Prestress> prestress)
        {
            // Create a free length variation array by adding up all prestress for each element.
            double[] freeLengthVariation = PrestressEncoder.AddsUpAllPrestress(prestress, truss.Elements.Count);
            
            // Call the core solver 
            var coreResult = MuscleCore.Solvers.LinearDM.Solve(TrussEncoder.ToCore(truss), loadsIncrement, freeLengthVariation);
            
            // Update the structure with the results
            if (coreResult == null)
                return null;
                
            var updatedTruss = TrussDecoder.CopyAndUpdate(truss, coreResult);
            
            return updatedTruss;
        }
    }
}
