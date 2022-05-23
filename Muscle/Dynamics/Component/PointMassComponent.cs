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
            pManager.AddIntegerParameter("Node Index", "Node", "Index of the node where the mass is applied.", GH_ParamAccess.list);
            pManager.AddNumberParameter("Mass", "M (kg)", "Number representing the mass in kg.", GH_ParamAccess.list);
        
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Point mass", "Mass (kg)", "Dynamic Mass applied on a point.", GH_ParamAccess.list);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            
            int ind = -1;
            
            List<int> PointIndex = new List<int>();
            if (!DA.GetDataList(0, PointIndex)) { return; }

            
            List<double> mass = new List<double>(); //Value of the mass
            if (!DA.GetDataList(1, mass)) { return; }

            
            List<GH_PointLoad> Return = new List<GH_PointLoad>();

            if (mass.Count != PointIndex.Count)
            {
                DA.SetData(0, null);
            }

            for (int i = 0; i < mass.Count; i++)
            {
                Vector3d vector = new Vector3d();
                vector.Z = mass[i];
                Return.Add(new GH_PointLoad(new PointLoad(PointIndex[i], vector)));
            }
            DA.SetDataList(0, Return);
        }

        #endregion Methods
    }
}