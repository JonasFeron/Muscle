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
            pManager.AddGenericParameter("Point", "P", "Point or Node or Index of the node where the load is applied. If input is an index, the load preview will not work, but the load will be added on the structure through a solver component.", GH_ParamAccess.item);
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

            PointLoad load = null;

            if (obj.Value is Node) //input is a node
            {
                Node node = obj.Value as Node;
                load = new PointLoad(node, vector);
            }

            if (obj.Value is GH_Point) //input is a point
            {
                Point3d point = (obj.Value as GH_Point).Value;
                load = new PointLoad(point, vector);
            }
            if (obj.Value is Point3d) //input is a point
            {
                Point3d point = (Point3d)obj.Value;
                load = new PointLoad(point, vector);
            }

            GH_Integer gh_ind = new GH_Integer();
            if (gh_ind.CastFrom(obj.Value))
            {
                int ind = gh_ind.Value;
                load = new PointLoad(ind, vector);
            }

            if (load == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Input must be a Node, Point3d, or index");
                return;
            }
            if (!load.IsValid)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Invalid load");
                return;
            }
            DA.SetData(0, new GH_PointLoad(load));
        }

        #endregion Methods
    }
}