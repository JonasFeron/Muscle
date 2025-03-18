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

namespace MuscleCore.Solvers
{
    public static class SVD
    {
        /// <summary>
        /// Solve the singular value decomposition for a structure with incremental loads and prestress (free length changes).
        /// </summary>
        /// <param name="structure">Current structure state</param>
        /// <param name="rtol">Tolerance for considering singular values as zero, relative to the highest singular value</param>
        /// <returns>SVDresults object containing the SVD results</returns>
        public static CoreResultsSVD? Solve(CoreTruss structure, double rtol)
        {
            string pythonPackage = "MusclePy"; 
            CoreResultsSVD? svdResults = null;

            var m_threadState = PythonEngine.BeginAllowThreads();
            using (Py.GIL())
            {
                try
                {
                    PyObject pyStructure = structure.ToPython();
                    dynamic musclepy = Py.Import(pythonPackage);
                    dynamic solve = musclepy.main_singular_value_decomposition;
                    dynamic pysvdResults = solve(
                        pyStructure,
                        rtol
                    );
                    svdResults = pysvdResults.As<CoreResultsSVD>();
                }
                catch (Exception e)
                {
                    throw;
                }
            }
            PythonEngine.EndAllowThreads(m_threadState);

            return svdResults;
        }
    }
}
