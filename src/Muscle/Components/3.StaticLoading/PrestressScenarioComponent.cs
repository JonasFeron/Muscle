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

using System;
using System.Collections.Generic;
using Grasshopper.Kernel;
using Rhino.Geometry;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.View;
using MuscleApp.ViewModel;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.StaticLoading
{
    public class PrestressScenarioComponent : GH_Component
    {

        public PrestressScenarioComponent()
          : base("Construct Prestress", "P",
              "Set the free lengths variation to apply on the elements through mechanical devices.",
              GHAssemblyName, Folder3_StaticLoading)
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
            get { return new Guid("ae51905c-0c73-48bd-b9d3-17c27c45c8de"); }
        }


        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "Element (General, Bar, Strut, or Cable) subjected to a prestress load.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Free length variation", "dL0 (m)", "Free length variation in m (+ lengthening, - shortening) to apply on the element.", GH_ParamAccess.item);

        }


        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Prestress", "P", "Prestress Scenario containing the free length variations to apply on the specified elements.", GH_ParamAccess.item);
        }


        protected override void SolveInstance(IGH_DataAccess DA)
        {
            //1) Collect Data
            GH_Element gh_e = new GH_Element();
            double value = 0.0;

            if (!DA.GetData(0, ref gh_e)) { return; }
            if (!DA.GetData(1, ref value)) { return; }

            Element e = gh_e.Value;

            //2) Transform datas into Prestress object
            Prestress P = new Prestress(e, value);

            //3) output datas
            DA.SetData(0, new GH_Prestress(P));

        }
    }
}
