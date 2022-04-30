using Grasshopper.Kernel;
using Rhino.Geometry;
using System;

namespace Muscle.Loads
{
    public class PointLoadPropertiesComponent : GH_Component
    {
        public PointLoadPropertiesComponent() :
            base("Point load properties", "Load Prop", "Get the properties of a point load", "Muscles", "Loads")
        {
        }

        public override Guid ComponentGuid { get { return new Guid("8f9096b4-a3d5-48de-a1f5-561d5707c2eb"); } }

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Point Load", "Load (kN)", "Load", GH_ParamAccess.item);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddPointParameter("Point", "P", "Point of application of the load.", GH_ParamAccess.item);
            pManager.AddVectorParameter("Vector", "V (kN)", "Vector representing the load in kN.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            GH_PointLoad ghPointLoad = new GH_PointLoad();

            if (!DA.GetData(0, ref ghPointLoad)) { return; }

            DA.SetData(0, ghPointLoad.Value.Point);
            DA.SetData(1, ghPointLoad.Value.Vector * 1e-3);
        }
    }
}

