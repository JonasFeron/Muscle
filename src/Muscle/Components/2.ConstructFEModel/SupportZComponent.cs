using Grasshopper.Kernel;
using Rhino.Geometry;
using System;


namespace Muscle.Components.CreateModel
{
    public class SupportZComponent : GH_Component
    {

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("eb860698-c0c1-473a-9bb2-b15243a2125c"); } }

        #endregion Properties

        #region Constructors

        public SupportZComponent() : base("Support Z", "SptZ",
                                                  "Set the Z support condition of a point",
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
            pManager.AddGenericParameter("Support", "Spt", "The given point can not move in the Z direction", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Point3d point = new Point3d();

            if (!DA.GetData(0, ref point)) { return; }

            DA.SetData(0, new GH_Support(new Support(point, true, true, false)));
        }

        #endregion Methods

    }
}