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
using Grasshopper.Kernel;
using MuscleApp.ViewModel;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.DeconstructFEModel
{
    public class DeconstructCSComponent : GH_Component
    {
        public DeconstructCSComponent() : base("Deconstruct Cross Section", "DeCS", "Deconstruct a Cross Section to retrieve its properties.", GHAssemblyName, Folder5_DeconstructFEM) { }

        public override Guid ComponentGuid { get { return new Guid("f78a23a7-1eb7-4b2c-8b0b-e88af4e0ebea"); } }

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Cross Section", "CS", "A cross section.", GH_ParamAccess.item);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddNumberParameter("Dimension", "D (mm)", "Principal outer dimension of the section in mm.\nDiameter for circle and width for square.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Thickness", "t (mm)", "Wall Thickness of the section in mm.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Dimension/Thickness", "D/t (-)", "Ratio Dimension/Thickness of the section.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Area", "A (mm2)", "Area of the section in mm^2.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Inertia", "I (mm4)", "Inertia of the section in mm^4", GH_ParamAccess.item);
            pManager.AddNumberParameter("q = I/A^2", "q (-)", "Ratio Inertia/Area^2 of the section.", GH_ParamAccess.item);

        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            ICrossSection CS = null;

            if (!DA.GetData(0, ref CS)) { return; }

            DA.SetData(0, CS.Dimension * 1e3);
            DA.SetData(1, CS.Thickness * 1e3);
            DA.SetData(2, CS.DoverT);
            DA.SetData(3, CS.Area * 1e6);
            DA.SetData(4, CS.Inertia * 1e12);
            DA.SetData(5, CS.q);
        }
    }
}
