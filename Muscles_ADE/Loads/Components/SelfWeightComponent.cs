using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscles_ADE.Elements;
using Rhino.Geometry;
using System;
using System.Collections.Generic;

namespace Muscles_ADE.Loads
{
    public class SelfWeightComponent : GH_Component
    {
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("0ad64607-0a74-4d68-b4ff-83a52615782e"); } }

        #endregion Properties

        #region Constructors

        public SelfWeightComponent() :
                    base("Self Weight", "SW", "Creates Points loads due to self-weight of the elements", "Muscles", "Loads")
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Elements", "E", "Generate self-weight loads applied on the extrimities of the given elements.", GH_ParamAccess.item);
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("SelfWeight loads", "Loads (kN)", "Point loads due to self-weight. Half of the element's self weight is applied on each of both extremities. ", GH_ParamAccess.list);
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
