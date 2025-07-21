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
using MuscleApp.Converters;
using MuscleCore.Solvers;

namespace MuscleApp.Solvers
{
    public static class DynamicModalAnalysis
    {
        /// <summary>
        /// Solve the linear displacement method for a structure with incremental loads and prestress (free length changes).
        /// </summary>
        /// <param name="truss">Current structure state</param>
        /// <param name="pointMasses">Collection of PointMass instances defining point masses to apply on the nodes</param>
        /// <param name="elementMass">Collection of double values defining the mass of each element</param>
        /// <returns>Updated Truss with incremented state</returns>
        public static ResultsDynamic? Solve(Truss truss, IEnumerable<PointMass> pointMasses, IEnumerable<double> elementMasses, int elementMassesOption, int nModes)
        {
            // 1) Convert the input data to the core data types
            // Create a pointmasses array by adding up all point loads for each node.
            double[] pointMassArray = PointMassEncoder.AddsUpAllPointMasses(pointMasses, truss);

            // 2) Call the core solver 
            CoreResultsDynamic? coreResults = MuscleCore.Solvers.DynamicModalAnalysis.Solve(TrussEncoder.ToCore(truss), pointMassArray, elementMasses.ToArray(), elementMassesOption, nModes);
            
            return new ResultsDynamic(coreResults);
        }
    }
}
