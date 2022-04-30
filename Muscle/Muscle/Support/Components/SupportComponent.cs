using Grasshopper.Kernel;
using Rhino.Geometry;
using System;

namespace Muscle
{
    public class SupportComponent : GH_Component
    {

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("026e10fe-1591-4efa-9af5-a1d3f65c7071"); } }

        public override bool IsPreviewCapable { get { return true; } }

        #endregion Properties

        #region Constructors

        public SupportComponent() : base("Support", "Spt", "Set the X Y Z support conditions of a point", "Muscles", "Model")
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
