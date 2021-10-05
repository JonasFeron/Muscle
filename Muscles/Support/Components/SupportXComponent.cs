using Grasshopper.Kernel;
using Rhino.Geometry;
using System;

namespace Muscles
{
    public class SupportXComponent :GH_Component
    {

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("c02e6a93-c786-400e-a3da-c1d3412fdefa"); } }

        #endregion Properties

        #region Constructors

        public SupportXComponent() : base("Support X", "SptX",
                                                  "Set the X support condition of a point",
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
            pManager.AddGenericParameter("Support", "Spt", "The given point can not move in the X direction", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            //string assemblyFolder = Environment.GetFolderPath(Environment.SpecialFolder.ApplicationData);
            //Rhino.RhinoApp.WriteLine("Location");
            //Rhino.RhinoApp.WriteLine(assemblyFolder);

            Point3d point = new Point3d( );

            if (!DA.GetData(0, ref point)) { return; }

            DA.SetData(0, new GH_Support(new Support(point, false, true, true)));
        }

        #endregion Methods

    }
}