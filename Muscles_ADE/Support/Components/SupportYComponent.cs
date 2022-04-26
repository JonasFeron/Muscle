using Grasshopper.Kernel;
using Rhino.Geometry;
using System;


namespace Muscles_ADE
{
    public class SupportYComponent : GH_Component
    {

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("81b47eda-3b1c-4a8b-8c12-9fadcc947b57"); } }

        #endregion Properties

        #region Constructors

        public SupportYComponent() : base("Support Y", "SptY",
                                                  "Set the Y support condition of a point",
                                          "Muscles", "Model")
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
