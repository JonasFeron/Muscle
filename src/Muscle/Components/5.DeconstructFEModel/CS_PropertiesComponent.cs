using System;
using Grasshopper.Kernel;
using Muscle.ViewModel;


namespace Muscle.Components.DeconstructFEModel
{
    public class CS_PropertiesComponent : GH_Component
    {
        public CS_PropertiesComponent() : base("Cross Section - Properties", "CS Prop", "Get the properties of a Cross Section", "Muscles", "Elements") { }

        public override Guid ComponentGuid { get { return new Guid("f78a23a7-1eb7-4b2c-8b0b-e88af4e0ebea"); } }

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Cross Section", "CS", "A cross section.", GH_ParamAccess.item);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddNumberParameter("Dimension", "D (mm)", "Principal outer dimension of the section in mm.\nDiameter for circle and width for square.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Thickness", "t (mm)", "Wall Thickness of the section in mm.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Dimension/Thickness", "D/t (-)", "Ratio Dimension/Thickness of the section.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Area", "A (mm2)", "Area of the section in mm^2.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Inertia", "I (mm4)", "Inertia of the section in mm^4", GH_ParamAccess.item);
            pManager.AddNumberParameter("q = I/A^2", "q (-)", "Ratio Inertia/Area^2 of the section.", GH_ParamAccess.item);

        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            ICrossSection CS = null;

            if (!DA.GetData(0, ref CS)) { return; }

            DA.SetData(0, CS.Dimension * 1e3);
            DA.SetData(1, CS.Thickness * 1e3);
            DA.SetData(2, CS.DoverT);
            DA.SetData(3, CS.Area * 1e6);
            DA.SetData(4, CS.Inertia * 1e12);
            DA.SetData(5, CS.q);
        }
    }
}
