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
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;
using Muscle.View;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.StaticLoading
{
    public class SelfWeightComponent : GH_Component
    {
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("e932fb12-0cf3-45d5-ae98-94c2ac38300d"); } }

        #endregion Properties

        #region Constructors

        public SelfWeightComponent() :
                    base("Self Weight", "SW", "Create Points loads due to self-weight of the elements",GHAssemblyName, Folder3_StaticLoading)

        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Elements", "E", "Generate self-weight loads applied on the end nodes of the given elements.", GH_ParamAccess.item);
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("SelfWeight loads", "Loads (kN)", "Point loads due to self-weight. Half of the element's self weight is applied on each of both end nodes.", GH_ParamAccess.list);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();
            if (!DA.GetData(0, ref e)) { return; }

            List<GH_PointLoad> selfweights = new List<GH_PointLoad>();

            GH_PointLoad p0 = new GH_PointLoad(new PointLoad(e.EndNodes[0], e.Weight / 2));
            GH_PointLoad p1 = new GH_PointLoad(new PointLoad(e.EndNodes[1], e.Weight / 2));
            selfweights.Add(p0);
            selfweights.Add(p1);

            DA.SetDataList(0, selfweights);
        }

        #endregion Methods
    }
}
