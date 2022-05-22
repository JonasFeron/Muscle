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

        public override Guid ComponentGuid { get { return new Guid("c3a3a37b-829b-46d1-a4b8-4a3d99ba614d"); } }

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
            pManager.AddGenericParameter("SelfMass", "Mass (kg)", "Point mass due to self-mass. Half of the element's self weight is applied on each of both extremities. ", GH_ParamAccess.list);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();
            if (!DA.GetData(0, ref e)) { return; }

            List<GH_PointLoad> selfmass = new List<GH_PointLoad>();
            double acc = AccessToAll.g.Z;
            GH_PointLoad p0 = new GH_PointLoad(new PointLoad(e.EndNodes[0], 1000*e.Weight / (2*acc))); //Because the weight is in kN : *1000
            GH_PointLoad p1 = new GH_PointLoad(new PointLoad(e.EndNodes[1], 1000*e.Weight / (2*acc)));
            selfmass.Add(p0);
            selfmass.Add(p1);

            DA.SetDataList(0, selfmass);
        }

        #endregion Methods
    }
}

