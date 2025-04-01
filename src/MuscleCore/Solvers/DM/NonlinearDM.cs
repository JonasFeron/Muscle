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

using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Solvers
{
    public static class NonlinearDM
    {
        /// <summary>
        /// Solve the nonlinear displacement method for a structure with incremental loads.
        /// </summary>
        /// <param name="coreInitial">Current structure state</param>
        /// <param name="loadsIncrement">[N] - shape (3*nodes.count,) - External load increments to apply</param>
        /// <param name="nSteps"> Number of steps for the incremental (but not iterative) Newton-Raphson procedure with arc length control</param>
        /// <returns>Updated CoreTruss with incremented state</returns>
        public static CoreTruss? Solve(CoreTruss coreInitial, double[] loadsIncrement, int nSteps)
        {
            CoreTruss? coreResult = null;
            try
            {
                var m_threadState = PythonEngine.BeginAllowThreads();
                using (Py.GIL())
                {
                    PyObject pyInitial = coreInitial.ToPython();

                    dynamic musclepy = Py.Import("MusclePy");
                    dynamic solve = musclepy.main_nonlinear_displacement_method;
                    dynamic pyResult = solve(
                        pyInitial,
                        loadsIncrement,
                        nSteps
                    );
                    coreResult = pyResult.As<CoreTruss>();
                }
                PythonEngine.EndAllowThreads(m_threadState);
            }
            catch (Exception)
            {
                throw; // rethrow the exception
            }
            return coreResult;
        }
    }
}
