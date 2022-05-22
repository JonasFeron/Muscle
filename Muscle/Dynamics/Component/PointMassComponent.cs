using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Muscle.Nodes;
using Rhino.Geometry;
using Muscle.Dynamics;
using Muscle.Elements;

namespace Muscle.Dynamics
{
    public class PointMassComponent : GH_Component
    {
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("7621c1b7-948d-4662-86e1-530c3dc19e5a"); } }

        #endregion Properties

        #region Constructors

        public PointMassComponent() :
                    base("Point mass", "Mass", "Create a Point mass by defining a vector", "Muscles", "Dynamics")
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            //pManager.AddGenericParameter("Point", "P", "Node where the mass is applied. Component work in the 3 cases but the preview only work if input is a point.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Point", "P", "Index of the node where the mass is applied.", GH_ParamAccess.item);
            pManager.HideParameter(0);
            
            pManager.AddNumberParameter("Mass", "M (kg)", "Number representing the mass in kg.", GH_ParamAccess.item);
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Point mass", "Mass (kg)", "Dynamic Mass applied on a point.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Point3d point = new Point3d();
            int ind = -1;
            //Node node = new Node();
            GH_ObjectWrapper obj = new GH_ObjectWrapper();
            if (!DA.GetData(0, ref obj)) { return; }

            Vector3d vector = new Vector3d();
            double mass = new double(); //Value of the mass
            if (!DA.GetData(1, ref mass)) { return; }

            vector.Z = mass;
            /*
            if (obj.Value is Node) //input is a node
            {
                ind = (obj.Value as Node).Ind;
                DA.SetData(0, new GH_PointLoad(new PointLoad(ind, vector)));
                return;
            }

            if (obj.Value is GH_Point) //input is a node
            {
                point = (obj.Value as GH_Point).Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(point, vector)));
                return;
            }
            if (obj.Value is Point3d) //input is a node
            {
                point = (Point3d)obj.Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(point, vector)));
                return;
            }
            */
            GH_Integer gh_ind = new GH_Integer();
            if (gh_ind.CastFrom(obj.Value))
            {
                ind = gh_ind.Value;
                DA.SetData(0, new GH_PointLoad(new PointLoad(ind, vector)));
                return;
            }
        }

        #endregion Methods
    }
}