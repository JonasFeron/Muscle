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
using MuscleCore.Solvers;
using MuscleCore.PythonNETInit;
using MuscleApp.ViewModel;
using MuscleApp.Solvers;
using Muscle.View;
using Muscle.Converters;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Solvers
{
    public class DRSolverComponent : GH_Component
    {

        private static CoreConfigDR defaultConfig = new CoreConfigDR();
        private static double default_dt = defaultConfig.Dt;
        private static double default_rtol = defaultConfig.ZeroResidualRTol;
        private static double default_atol = defaultConfig.ZeroResidualATol;
        private static int default_maxTimeStep = defaultConfig.MaxTimeStep;
        private static int default_maxPeakReset = defaultConfig.MaxKEResets;
        private static double default_amplMass = defaultConfig.MassAmplFactor;
        private static double default_minMass = defaultConfig.MinMass;

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DRSolverComponent()
          : base("Dynamic Relaxation Method", "DR",
                "Solve form-finding, deployment, nonlinear loading, and nonlinear prestressing problems",
              GHAssemblyName, Folder4_StaticSolvers)
        {
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("c040d80e-f794-455d-8f4f-9d82c5b59913"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure on which the point loads and prestress will be applied via the dynamic relaxation method.", GH_ParamAccess.item);
            pManager.AddGenericParameter("Point Loads", "Load (kN)", "The external point loads to apply on the structure.", GH_ParamAccess.tree);
            pManager.AddGenericParameter("Prestress", "P (m)", "Prestress Scenario containing the free length variations (m) to apply on the specified elements.", GH_ParamAccess.tree);
            pManager.AddNumberParameter("Relative tolerance", "rtol (-)", "Set the relative tolerance for equilibrium. Equilibrium is achieved if each residual load is equal to 0 [N] (within tolerance : rtol * load + atol).", GH_ParamAccess.item, default_rtol);
            pManager.AddNumberParameter("Absolute tolerance", "atol (N)", "Set the absolute tolerance for equilibrium. Equilibrium is achieved if each residual load is equal to 0 [N] (within tolerance : rtol * load + atol).", GH_ParamAccess.item, default_atol);
            pManager.AddNumberParameter("Delta t", "Dt (s)", "The time increment for the dynamic relaxation method.", GH_ParamAccess.item, default_dt);
            pManager.AddIntegerParameter("Max Time Step", "max it (-)", "Maximum number of time increment before the solver aborts looking for the equilibrium", GH_ParamAccess.item, default_maxTimeStep);
            pManager.AddIntegerParameter("Max Peak Reset", "max peak (/)", "Maximum number of kinetic energy resets before the solver aborts looking for the equilibrium.", GH_ParamAccess.item, default_maxPeakReset);
            pManager.AddNumberParameter("Mass Amplification", "Ampl (/)", "Amplification factor for the fictitious masses in case of convergence issue.", GH_ParamAccess.item, default_amplMass);
            pManager.AddNumberParameter("Minimum Mass", "Min (kg)", "Minimum fictitious mass applied on the degrees of freedom where fictitious mass equals 0 (i.e. 0 tangent stiffness).", GH_ParamAccess.item, default_minMass);

            pManager[1].Optional = true;
            pManager[2].Optional = true;
            pManager[3].Optional = true;
            pManager[4].Optional = true;
            pManager[5].Optional = true;
            pManager[6].Optional = true;
            pManager[7].Optional = true;
            pManager[8].Optional = true;
            pManager[9].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure containing the total results.", GH_ParamAccess.item);
            pManager.AddBooleanParameter("IsInEquilibrium", "Equilibrium", "True if the external load are in equilibrium with the internal forces.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Time Step", "it (/)", "The number of time increments required to reach the equilibrium", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Peak Reset", "peaks (/)", "The number of detected peaks at which the kinetic energy has been reset to 0", GH_ParamAccess.item);
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

            //1) Collect Data
            GH_Truss gh_truss = new GH_Truss();
            GH_Structure<IGH_Goo> gh_loads = new GH_Structure<IGH_Goo>();
            GH_Structure<IGH_Goo> gh_prestress = new GH_Structure<IGH_Goo>();
            double rtol = -1;
            double atol = -1;
            double dt = -1;
            int maxTimeStep = -1;
            int maxKEReset = -1;
            double amplMass = -1;
            double minMass = -1;

            if (!DA.GetData(0, ref gh_truss)) { return; }
            if (!DA.GetDataTree(1, out gh_loads)) { }
            if (!DA.GetDataTree(2, out gh_prestress)) { }
            if (!DA.GetData(3, ref rtol)) { }
            if (!DA.GetData(4, ref atol)) { }
            if (!DA.GetData(5, ref dt)) { }
            if (!DA.GetData(6, ref maxTimeStep)) { }
            if (!DA.GetData(7, ref maxKEReset)) { }
            if (!DA.GetData(8, ref amplMass)) { }
            if (!DA.GetData(9, ref minMass)) { }

           // 2) Transform data before solving 
            Truss truss = gh_truss.Value;
            List<PointLoad> pointLoads = GH_Decoders.ToPointLoadList(gh_loads);
            List<Prestress> prestress = GH_Decoders.ToPrestressList(gh_prestress);
            CoreConfigDR user_config = new CoreConfigDR
            {
                Dt = dt,
                MassAmplFactor = amplMass,
                MinMass = minMass,
                MaxTimeStep = maxTimeStep,
                MaxKEResets = maxKEReset,
                ZeroResidualRTol = rtol,
                ZeroResidualATol = atol
            };


            // Check if we have any loads or prestress to apply
            if (pointLoads.Count == 0 && prestress.Count == 0)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "No loads or prestress provided. The structure will not change.");
                DA.SetData(0, gh_truss);
                return;
            }

            Truss result = null;
            // 3) Solve using the LinearDM solver
            try
            {
                result = MuscleApp.Solvers.DynamicRelaxation.Solve(truss, pointLoads, prestress, user_config);
            }
            catch (Exception e)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Failed to solve the dynamic relaxation method: {e.Message}");
                return;
            }

            // 4) Check if the solution was successful
            if (result == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to solve the dynamic relaxation method.");
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
            DA.SetData(1, result.IsInEquilibrium);
            DA.SetData(2, user_config.NTimeStep);
            DA.SetData(3, user_config.NKEReset);

        }
    }
}
