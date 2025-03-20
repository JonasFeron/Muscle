using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;
using Muscle.View;
using Rhino.Geometry;
using System;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.StaticLoading
{
    public class PointLoadComponent : GH_Component
    {
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("d7f0fcb1-3c16-432e-929f-31cadc236980"); } }

        #endregion Properties

        #region Constructors

        public PointLoadComponent() :
                    base("Point load", "Load", "Create a Point load by defining a vector.", GHAssemblyName, Folder3_StaticLoading)
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
            GH_ObjectWrapper obj = new GH_ObjectWrapper();
            Vector3d vector = new Vector3d();

            if (!DA.GetData(0, ref obj)) { return; }
            if (!DA.GetData(1, ref vector)) { return; }

            // Scale vector to N (assuming input is in kN)
            vector *= 1e3;

            if (obj.Value is Node) //input is a node
            {
                int ind = (obj.Value as Node).Idx;
                DA.SetData(0, new GH_PointLoad(new PointLoad(ind, vector)));
                return;
            }

            if (obj.Value is GH_Point) //input is a node
            {
                Point3d point = (obj.Value as GH_Point).Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(point, vector)));
                return;
            }
            if (obj.Value is Point3d) //input is a node
            {
                Point3d point = (Point3d)obj.Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(point, vector)));
                return;
            }

            GH_Integer gh_ind = new GH_Integer();
            if (gh_ind.CastFrom(obj.Value))
            {
                int ind = gh_ind.Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(ind, vector)));
                return;
            }

            // If we get here, we couldn't handle the input
            AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Input must be a Node, Point3d, or index");
        }

        #endregion Methods
    }
}