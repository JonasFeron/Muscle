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
    public class SupportXComponent : GH_Component
    {

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("c02e6a93-c786-400e-a3da-c1d3412fdefa"); } }

        #endregion Properties

        #region Constructors

        public SupportXComponent() : base("Construct Support X", "SptX",
                                                  "Set the X support condition of a point",
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
            pManager.AddGenericParameter("Support", "Spt", "The given point can not move in the X direction", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            //string assemblyFolder = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            //Rhino.RhinoApp.WriteLine("Location");
            //Rhino.RhinoApp.WriteLine(assemblyFolder);

            Point3d point = new Point3d();

            if (!DA.GetData(0, ref point)) { return; }

            DA.SetData(0, new GH_Support(new Support(point, false, true, true)));
        }

        #endregion Methods

    }
}