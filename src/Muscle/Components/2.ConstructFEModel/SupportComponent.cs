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
using Muscle.View;
using MuscleApp.ViewModel;
using Rhino.Geometry;
using System;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.ConstructFEModel
{
    public class SupportComponent : GH_Component
    {

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("f76b8abc-92ab-4995-83fc-a50bc1e6bf8c"); } }

        public override bool IsPreviewCapable { get { return true; } }

        #endregion Properties

        #region Constructors

        public SupportComponent() : base("Construct Support", "Spt", "Set the X Y Z support conditions of a point", GHAssemblyName, Folder2_ConstructFEM)
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddPointParameter("Point", "Pt", "Point(s) of application of the support", GH_ParamAccess.item); //if a list of point is given, the solve instance will be called on each point
            pManager.AddBooleanParameter("IsXFree", "X", "Is the X direction free to move ?", GH_ParamAccess.item, false);
            pManager.AddBooleanParameter("IsYFree", "Y", "Is the Y direction free to move ?", GH_ParamAccess.item, false);
            pManager.AddBooleanParameter("IsZFree", "Z", "Is the Z direction free to move ?", GH_ParamAccess.item, false);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Support", "Spt", "The given point can not move in the given directions", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Point3d point = new Point3d();
            bool isXfree = false;
            bool isYfree = false;
            bool isZfree = false;

            if (!DA.GetData(0, ref point)) { return; }
            if (!DA.GetData(1, ref isXfree)) { return; }
            if (!DA.GetData(2, ref isYfree)) { return; }
            if (!DA.GetData(3, ref isZfree)) { return; }
            Support support = new Support(point, isXfree, isYfree, isZfree);
            GH_Support gh_support = new GH_Support(support);
            DA.SetData(0, gh_support);
        }

        #endregion Methods

    }
}
