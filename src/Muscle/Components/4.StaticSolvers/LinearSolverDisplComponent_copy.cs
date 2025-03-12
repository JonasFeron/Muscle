//this file is based on the template https://github.com/JonasFeron/PythonNETGrasshopperTemplate 
//------------------------------------------------------------------------------------------------------------

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

//this file was imported from https://github.com/JonasFeron/PythonConnectedGrasshopperTemplate and is used WITH modifications.
//------------------------------------------------------------------------------------------------------------

//Copyright < 2021 - 2025 > < Université catholique de Louvain (UCLouvain)>

//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.

//List of the contributors to the development of PythonConnectedGrasshopperTemplate: see NOTICE file.
//Description and complete License: see NOTICE file.
//------------------------------------------------------------------------------------------------------------


using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Python.Runtime;
using Muscle.FEModel;
using Rhino.Geometry;
using Muscle.ViewModel;
using Muscle.GHModel;

namespace Muscle.Solvers.Components
{
    public class LinearSolverDisplComponent : GH_Component
    {
        public LinearSolverDisplComponent()
          : base("Linear Solver Displacement", "LinSolverDispl",
              "Solve a linear problem with displacement method",
              "Muscle", "Solvers")
        {
        }

        public override Guid ComponentGuid
        {
            get { return new Guid("YOUR-GUID-HERE"); }
        }

        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may contain previous results (forces and displacements).", GH_ParamAccess.item);
            pManager.AddGenericParameter("External Point Loads", "Le (kN)", "The external point loads to apply on the structure.", GH_ParamAccess.tree);
            pManager.AddGenericParameter("Length Variation", "DL (m)", "Lengthening (+) or shortening (-) to apply on the elements.", GH_ParamAccess.tree);
            pManager[1].Optional = true;
            pManager[2].Optional = true;
        }

        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure containing the results (forces and displacements).", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string pythonScript = "MainLinearSolveStructure";
            if (!AccessToAll.hasPythonStarted)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }
            if (!File.Exists(Path.Combine(AccessToAll.pythonProjectDirectory, pythonScript + ".py")))
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Please ensure that \"{pythonScript}\" is located in: {AccessToAll.pythonProjectDirectory}");
                DA.SetData(0, null);
                return;
            }

            // 1) Collect Data
            StructureObj structure = new StructureObj();
            GH_Structure<IGH_Goo> gh_loads_ext = new GH_Structure<IGH_Goo>();
            GH_Structure<IGH_Goo> gh_loads_prestress = new GH_Structure<IGH_Goo>();

            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetDataTree(1, out gh_loads_ext)) { }
            if (!DA.GetDataTree(2, out gh_loads_prestress)) { }

            // 2) Transform data before solving in python
            StructureObj new_structure = structure.Duplicate();

            bool success1 = RegisterPointLoads(new_structure, gh_loads_ext.FlattenData());
            bool success2 = RegisterPrestressLoads(new_structure, gh_loads_prestress.FlattenData());

            if (!success1 && !success2)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to collect load data");
                return;
            }

            // 3) Convert to FEM model
            var femNodes = FEM_PythonConverter.ConvertToPythonFEMNodes(new_structure);
            var femElements = FEM_PythonConverter.ConvertToPythonFEMElements(new_structure);

            // 4) Solve in Python using Python.NET
            var m_threadState = PythonEngine.BeginAllowThreads();

            using (Py.GIL())
            {
                try
                {
                    dynamic script = Py.Import(pythonScript);
                    dynamic mainFunction = script.core;
                    
                    // Convert C# objects to Python objects
                    using (PyObject pyNodes = femNodes.ToPython())
                    using (PyObject pyElements = femElements.ToPython())
                    {
                        // Call Python function with direct object passing
                        dynamic result = mainFunction(pyNodes, pyElements);
                        
                        // Update structure with results
                        FEM_PythonConverter.UpdateStructureFromPythonResults(new_structure, result);
                    }
                }
                catch (PythonException ex)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, ex.Message);
                    return;
                }
                catch (Exception e)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                    return;
                }
            }
            PythonEngine.EndAllowThreads(m_threadState);

            // 5) Set output
            GH_StructureObj gh_structure = new GH_StructureObj(new_structure);
            DA.SetData(0, gh_structure);
        }

        private bool RegisterPointLoads(StructureObj structure, List<IGH_Goo> loads)
        {
            if (loads == null || loads.Count == 0) return false;

            for (int i = 0; i < structure.StructuralNodes.Count; i++)
            {
                if (i < loads.Count)
                {
                    GH_Vector load;
                    if (loads[i].CastTo<GH_Vector>(out load))
                    {
                        Vector3d v = load.Value;
                        structure.LoadsToApply[i] = new Point3d(v.X * 1000, v.Y * 1000, v.Z * 1000);
                    }
                }
            }
            return true;
        }

        private bool RegisterPrestressLoads(StructureObj structure, List<IGH_Goo> lengthenings)
        {
            if (lengthenings == null || lengthenings.Count == 0) return false;

            for (int i = 0; i < structure.StructuralElements.Count; i++)
            {
                if (i < lengthenings.Count)
                {
                    GH_Number lengthening;
                    if (lengthenings[i].CastTo<GH_Number>(out lengthening))
                    {
                        structure.LengtheningsToApply[i] = lengthening.Value;
                    }
                }
            }
            return true;
        }
    }
}