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
    /// <summary>
    /// Provides methods for performing dynamic modal analysis on structural models.
    /// </summary>
    public static class DynamicModalAnalysis
    {
        /// <summary>
        /// Performs dynamic modal analysis to compute natural frequencies and mode shapes of a structure.
        /// </summary>
        /// <param name="structure">The structure to analyze. The tangent stiffness matrix will be computed 
        /// based on the current state of the structure (including any preloading or self-stress).</param>
        /// <param name="pointMasses">Point masses in kg to be added at each node. Array length should match 
        /// the number of nodes multiplied by 3 (for X, Y, Z directions).</param>
        /// <param name="elementMasses">Element masses in kg. Array length should match the number of elements.</param>
        /// <param name="elementMassesOption">Option for handling element masses:
        /// 0: Neglect element masses (only point masses are considered)
        /// 1: Use lumped mass matrix (element mass is split between end nodes)
        /// 2: Use consistent mass matrix (more accurate but not diagonal)</param>
        /// <param name="nModes">Number of natural modes to compute. If 0 or greater than available DOFs,
        /// all possible modes will be computed.</param>
        /// <returns>CoreResultsDynamic object containing natural frequencies, mode shapes, and masses</returns>
        public static CoreResultsDynamic? Solve(CoreTruss structure, double[] pointMasses, double[] elementMasses, int elementMassesOption, int nModes)
        {
            string pythonPackage = "MusclePy"; 
            CoreResultsDynamic? dynamicResults = null;

            var m_threadState = PythonEngine.BeginAllowThreads();
            using (Py.GIL())
            {
                try
                {
                    PyObject pyStructure = structure.ToPython();
                    dynamic musclepy = Py.Import(pythonPackage);
                    dynamic solve = musclepy.main_dynamic_modal_analysis;
                    dynamic pydynamicResults = solve(
                        pyStructure,
                        pointMasses, 
                        elementMasses, 
                        elementMassesOption, 
                        nModes
                    );
                    dynamicResults = pydynamicResults.As<CoreResultsDynamic>();
                }
                catch (Exception)
                {
                    throw;
                }
            }
            PythonEngine.EndAllowThreads(m_threadState);

            return dynamicResults;
        }
    }
}
