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
using MuscleApp.ViewModel;
using Muscle.View;
using Muscle.Converters;
using MuscleApp.Solvers;

namespace Muscle.Solvers.Components
{
    public class LinearSolverDisplComponent_copy : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the LinearSolverDisplComponent class.
        /// </summary>
        public LinearSolverDisplComponent_copy()
          : base("Linear Displacement Method", "LinearDM",
              "Solve the linear displacement method for a structure with incremental loads and prestress (free length changes).",
              "Muscle", "4.StaticSolvers")
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
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

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // Check if Python.NET is initialized
            if (!Python.Runtime.PythonEngine.IsInitialized)
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
            GH_Truss gh_truss = new GH_Truss();
            GH_Structure<IGH_Goo> gh_loads = new GH_Structure<IGH_Goo>();
            GH_Structure<IGH_Goo> gh_prestress = new GH_Structure<IGH_Goo>();

            if (!DA.GetData(0, ref gh_truss)) { return; }
            if (!DA.GetDataTree(1, out gh_loads)) { }
            if (!DA.GetDataTree(2, out gh_prestress)) { }

            // 2) Transform data before solving 
            Truss truss = gh_truss.Value;
            List<PointLoad> pointLoads = GH_Decoders.ToPointLoadList(gh_loads);
            List<Prestress> prestress = GH_Decoders.ToPrestressList(gh_prestress);

            // Check if we have any loads or prestress to apply
            if (pointLoads.Count == 0 && prestress.Count == 0)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "No loads or prestress provided. The structure will not change.");
                DA.SetData(0, gh_truss);
                return;
            }

            // 3) Solve using the LinearDM solver
            Truss? result = LinearDM.Solve(truss, pointLoads, prestress);

            // Check if the solution was successful
            if (result == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to solve the linear displacement method.");
                return;
            }

            // 4) Check for warnings from the solver
            if (result.warnings != null && result.warnings.Count > 0)
            {
                foreach (string warning in result.warnings)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, warning);
                }
                result.warnings.Clear();
            }

            // 5) Set output
            GH_Truss gh_result = new GH_Truss(result);
            DA.SetData(0, gh_result);
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                // You can add image files to your project resources and access them like this:
                //return Resources.IconForThisComponent;
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("2ec0d860-6029-4346-8925-49f2c69e132c"); }
        }
    }
}