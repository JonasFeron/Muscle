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

            if (obj.Value is IGH_Goo) //input is a GH_Goo object
            {
                // Extract the underlying value from the GH_Goo<T> object using reflection
                var ghGoo = obj.Value;
                Type gooType = ghGoo.GetType();
                var valueProperty = gooType.GetProperty("Value");
                
                if (valueProperty != null)
                {
                    object innerValue = valueProperty.GetValue(ghGoo, null);
                    
                    if (innerValue is Node)
                    {
                        Node node = innerValue as Node;
                        DA.SetData(0, new GH_PointLoad(new MuscleApp.ViewModel.PointLoad(node, vector * 1e3)));
                        return;
                    }
                    else if (innerValue is Point3d)
                    {
                        Point3d point = (Point3d)innerValue;
                        DA.SetData(0, new GH_PointLoad(new MuscleApp.ViewModel.PointLoad(point, vector * 1e3)));
                        return;
                    }
                }
            }

            if (obj.Value is GH_Point) //input is a node
            {
                Point3d point = (obj.Value as GH_Point).Value;
                DA.SetData(0, new GH_PointLoad(new MuscleApp.ViewModel.PointLoad(point, vector * 1e3)));
                return;
            }
            if (obj.Value is Point3d) //input is a node
            {
                Point3d point = (Point3d)obj.Value;
                DA.SetData(0, new GH_PointLoad(new MuscleApp.ViewModel.PointLoad(point, vector * 1e3)));
                return;
            }

            GH_Integer gh_ind = new GH_Integer();
            if (gh_ind.CastFrom(obj.Value))
            {
                int ind = gh_ind.Value;
                DA.SetData(0, new GH_PointLoad(new MuscleApp.ViewModel.PointLoad(ind, vector * 1e3)));
                return;
            }
        }

        #endregion Methods
    }
}