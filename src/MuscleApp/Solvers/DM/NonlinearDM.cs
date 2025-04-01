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
using MuscleApp.Converters;
using MuscleCore.FEModel;

namespace MuscleApp.Solvers
{
    public static class NonlinearDM
    {
        /// <summary>
        /// Solve the nonlinear displacement method for a structure with incremental loads.
        /// </summary>
        /// <param name="truss">Current structure state</param>
        /// <param name="pointLoads">Collection of PointLoad instances defining external loads to apply</param>
        /// <param name="nSteps"> Number of steps for the incremental (but not iterative) Newton-Raphson procedure with arc length control</param>
        /// <returns>Updated Truss with incremented state</returns>
        public static Truss? Solve(Truss truss, IEnumerable<PointLoad> pointLoads, int nSteps)
        {   
            // 1) Convert the input data to the core data types
            // Create a load increment array by adding up all point loads for each node.
            double[] loadsIncrement = PointLoadEncoder.AddsUpAllPointLoads(pointLoads, truss);

            // 2) Call the core solver 
            CoreTruss? coreResult = null;
            try{
                coreResult = MuscleCore.Solvers.NonlinearDM.Solve(TrussEncoder.ToCore(truss), loadsIncrement, nSteps);
            }
            catch (Exception)
            {
                throw; // rethrow the exception
            }

            // 3) Update the input structure with the results
            if (coreResult == null)
                return null;
            
            var updatedTruss = TrussDecoder.CopyAndUpdate(truss, coreResult);
            
            return updatedTruss;
        }
    }
}
