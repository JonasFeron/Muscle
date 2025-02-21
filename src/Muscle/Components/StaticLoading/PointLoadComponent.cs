using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Muscle.ViewModel;
using Rhino.Geometry;
using System;

namespace Muscle.Components.StaticLoading
{
    public class PointLoadComponent : GH_Component
    {
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("d7f0fcb1-3c16-432e-929f-31cadc236980"); } }

        #endregion Properties

        #region Constructors

        public PointLoadComponent() :
                    base("Point load", "Load", "Create a Point load by defining a vector", "Muscles", "Loads")
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Point", "P", "Point or Node or Index of the node where the load is applied. Component work in the 3 cases but the preview only work if input is a point.", GH_ParamAccess.item);
            pManager.HideParameter(0);
            pManager.AddVectorParameter("Vector", "V (kN)", "Vector representing the load in kN.", GH_ParamAccess.item);
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Point load", "Load (kN)", "External load applied on a point.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Point3d point = new Point3d();
            int ind = -1;
            //Node node = new Node();
            GH_ObjectWrapper obj = new GH_ObjectWrapper();
            if (!DA.GetData(0, ref obj)) { return; }

            Vector3d vector = new Vector3d();
            if (!DA.GetData(1, ref vector)) { return; }


            if (obj.Value is Node) //input is a node
            {
                ind = (obj.Value as Node).Ind;
                DA.SetData(0, new GH_PointLoad(new PointLoad(ind, vector * 1e3)));
                return;
            }

            if (obj.Value is GH_Point) //input is a node
            {
                point = (obj.Value as GH_Point).Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(point, vector * 1e3)));
                return;
            }
            if (obj.Value is Point3d) //input is a node
            {
                point = (Point3d)obj.Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(point, vector * 1e3)));
                return;
            }

            GH_Integer gh_ind = new GH_Integer();
            if (gh_ind.CastFrom(obj.Value))
            {
                ind = gh_ind.Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(ind, vector * 1e3)));
                return;
            }
        }

        #endregion Methods
    }
}