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

using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Application.PythonNETSolvers
{
    public static class LinearDMSolver
    {
        /// <summary>
        /// Solve the linear displacement method for a structure with incremental loads and prestress (free length changes).
        /// </summary>
        /// <param name="csInitialStruct">Current structure state</param>
        /// <param name="loadsIncrement">[N] - shape (3*nodes.count,) - External load increments to apply</param>
        /// <param name="deltaFreeLengthIncrement">[m] - shape (elements.count,) - Free length increments to apply</param>
        /// <returns>Updated FEM_Structure with incremented state</returns>
        public static FEM_Structure? Solve(FEM_Structure csInitialStruct, double[] loadsIncrement, double[] deltaFreeLengthIncrement)
        {
            string pythonPackage = "MusclePy"; 
            FEM_Structure? csDeformedStruct = null;

            var m_threadState = PythonEngine.BeginAllowThreads();
            using (Py.GIL())
            {
                try
                {
                    PyObject pyInitialStruct = csInitialStruct.ToPython();
                    dynamic musclepy = Py.Import(pythonPackage);
                    dynamic mainFunction = musclepy.main_linear_displacement_method;
                    dynamic pyDeformedStruct = mainFunction(
                        pyInitialStruct,
                        loadsIncrement,
                        deltaFreeLengthIncrement
                    );
                    csDeformedStruct = pyDeformedStruct.As<FEM_Structure>();
                }
                catch (Exception e)
                {
                    throw;
                }
            }
            PythonEngine.EndAllowThreads(m_threadState);

            return csDeformedStruct;
        }
    }
}
