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
    public static class FEM_ElementsInitializer
    {

        public static FEM_Elements? Initialize(FEM_Elements csElements)
        {
            FEM_Elements? csInitializedElements = null;

            var m_threadState = PythonEngine.BeginAllowThreads();
            using (Py.GIL())
            {
                try
                {
                    PyObject pyInitializedElements = csElements.ToPython(); // convert C# FEM_Elements to Python FEM_Elements to compute all the properties
                    csInitializedElements = pyInitializedElements.As<FEM_Elements>(); // retrieve in C# the properties that have been computed in python.
                }
                catch (Exception e)
                {
                    throw;
                }
            }
            PythonEngine.EndAllowThreads(m_threadState);

            return csInitializedElements;
        }
    }
}