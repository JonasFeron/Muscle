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

// PythonConnectedGrasshopperTemplate

// Copyright < 2021 - 2025 > < Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of PythonConnectedGrasshopperTemplate: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------


using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using Muscle.View;
using Muscle.Converters;
using MuscleApp.ViewModel;
using MuscleApp.Solvers;
using MuscleCore.PythonNETInit;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Solvers
{
    public class NonlinearDMSolverComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the NonlinearDMSolverComponent class.
        /// </summary>
        public NonlinearDMSolverComponent()
          : base("Non-linear Displacement Method", "Non linear DM",
              "Solve the non linear displacement method for a structure with incremental loads. This component solves an incremental (but not iterative) Newton-Raphson procedure with arc-length control method. Loads are splitted in +- nSteps increments, applied one after the other. The total number of increments may vary (in case of snap-through for instance) thanks to arc-length control. This solver does not support non-linear prestressing problems.",
              GHAssemblyName, Folder4_StaticSolvers)
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure on which the point loads will be applied incrementally via the non-linear displacement method.", GH_ParamAccess.item);
            pManager.AddGenericParameter("Point Loads", "Load (kN)", "The external point loads to apply on the structure.", GH_ParamAccess.tree);
            pManager.AddIntegerParameter("Number of increments", "nSteps", "Solve non-linearly the structure in +- nSteps increments", GH_ParamAccess.item, 50);
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
            if (!PythonNETManager.IsInitialized)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }

            // 1) Collect Data
            GH_Truss gh_truss = new GH_Truss();
            GH_Structure<IGH_Goo> gh_loads = new GH_Structure<IGH_Goo>();
            int nSteps = -1;

            if (!DA.GetData(0, ref gh_truss)) { return; }
            if (!DA.GetDataTree(1, out gh_loads)) { }
            if (!DA.GetData(2, ref nSteps)) { }

            // 2) Transform data before solving 
            Truss truss = gh_truss.Value;
            List<PointLoad> pointLoads = GH_Decoders.ToPointLoadList(gh_loads);

            // Check if we have any loads to apply
            if (pointLoads.Count == 0)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "No loads provided. The structure will not change.");
                DA.SetData(0, gh_truss);
                return;
            }

            // 3) Solve using the NonlinearDM solver
            Truss result = null;
            try
            {
                result = NonlinearDM.Solve(truss, pointLoads, nSteps);
            }
            catch (Exception e)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Failed to solve the non-linear displacement method: {e.Message}");
                return;
            }

            // 4) Check if the solution was successful
            if (result == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to solve the non-linear displacement method.");
                return;
            }

            // 5) Check for warnings from the solver
            if (result.warnings != null && result.warnings.Count > 0)
            {
                foreach (string warning in result.warnings)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, warning);
                }
                result.warnings.Clear();
            }

            // 6) Set output
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
            get { return new Guid("a5cd4c04-270f-4f9a-a948-0a4164e041ec"); }
        }
    }
}