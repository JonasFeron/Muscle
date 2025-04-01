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
using Muscle.View;
using MuscleApp.ViewModel;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.ConstructFEModel
{
    public class CS_CircularComponent : GH_Component
    {

        #region Constructors

        public CS_CircularComponent() : base("Construct Cross Section - Circular", "Circular CS", "Define a (hollow) circular cross-section", GHAssemblyName, Folder2_ConstructFEM) { }

        public override Guid ComponentGuid { get { return new Guid("f5fcd871-f31c-4a94-a249-467768a3e960"); } }
        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddNumberParameter("Diameter", "D (mm)", "Outer Diameter of the section in mm.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Thickness", "t (mm)", "Wall thickness of the section in mm. Full section if t=0 (default).", GH_ParamAccess.item, 0.0);
            pManager[1].Optional = true;
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Cross Section - Circular", "CS", "(Hollow) Circular Cross Section of given diameter and thickness", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            double diameter = 0.0;
            double thickness = 0.0;

            if (!DA.GetData(0, ref diameter)) { return; }
            if (!DA.GetData(1, ref thickness)) { }
            CS_Circular CS = new CS_Circular(diameter / 1e3, thickness / 1e3);

            DA.SetData(0, new GH_CrossSection(CS));
        }

        #endregion Methods
    }

    public class CS_SquareComponent : GH_Component
    {

        #region Constructors

        public CS_SquareComponent() : base("Construct Cross Section - Square", "Square CS", "Define a (hollow) square cross-section", GHAssemblyName, Folder2_ConstructFEM) { }
        public override Guid ComponentGuid { get { return new Guid("097eef62-fba6-4949-b39a-8d2abf8a5f6d"); } }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddNumberParameter("Width", "W (mm)", "Outer Width of the section in mm.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Thickness", "t (mm)", "Wall Thickness of the section in mm. Full section if t=0 (default).", GH_ParamAccess.item, 0.0);
            pManager[1].Optional = true;
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Cross Section - Square", "CS", "(Hollow) Square Cross Section of given width and thickness", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            double width = 0.0;
            double thickness = 0.0;

            if (!DA.GetData(0, ref width)) { return; }
            if (!DA.GetData(1, ref thickness)) { }

            DA.SetData(0, new GH_CrossSection(new CS_Square(width * 1e-3, thickness * 1e-3)));
        }

        #endregion Methods
    }
}
