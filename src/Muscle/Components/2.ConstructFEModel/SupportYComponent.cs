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

using Grasshopper.Kernel;
using Rhino.Geometry;
using System;
using Muscle.View;
using MuscleApp.ViewModel;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.ConstructFEModel
{
    public class SupportYComponent : GH_Component
    {

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("ebf75adf-4742-4a6c-9fff-adb7797d3cca"); } }

        #endregion Properties

        #region Constructors

        public SupportYComponent() : base("Construct Support Y", "SptY",
                                                  "Set the Y support condition of a point",
                                          GHAssemblyName, Folder2_ConstructFEM)
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddPointParameter("Point", "Pt", "Point(s) of application of the support", GH_ParamAccess.item);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Support", "Spt", "The given point can not move in the Y direction", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Point3d point = new Point3d();

            if (!DA.GetData(0, ref point)) { return; }

            DA.SetData(0, new GH_Support(new Support(point, true, false, true)));
        }

        #endregion Methods

    }
}