using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.Elements;
using Rhino.Geometry;
using System;
using System.Collections.Generic;

namespace Muscle.Dynamics
{
    public class SelfMassComponent : GH_Component
    {
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("3541fcf5-3ddc-46b3-92af-ad68c282a271"); } }

        #endregion Properties

        #region Constructors

        public SelfMassComponent() :
                    base("Self Mass", "SM", "Creates Points loads due to self-mass of the elements", "Muscles", "Dynamics")
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
            pManager.AddGenericParameter("SelfMass loads", "Loads (kN)", "Point loads due to self-mass. Half of the element's self weight is applied on each of both extremities. ", GH_ParamAccess.list);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();
            if (!DA.GetData(0, ref e)) { return; }

            List<GH_PointLoad> selfmass = new List<GH_PointLoad>();

            GH_PointLoad p0 = new GH_PointLoad(new PointLoad(e.EndNodes[0], e.Weight / 2));
            GH_PointLoad p1 = new GH_PointLoad(new PointLoad(e.EndNodes[1], e.Weight / 2));
            selfmass.Add(p0);
            selfmass.Add(p1);

            DA.SetDataList(0, selfmass);
        }

        #endregion Methods
    }
}

