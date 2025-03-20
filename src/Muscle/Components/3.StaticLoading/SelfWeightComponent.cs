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
