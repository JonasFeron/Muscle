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
                    base("Point Mass", "PM", "Create one or more point mass(es). Those point masses are used for the dynamic computation.", "Muscles", "Dynamics")
        {
        }

        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //return Properties.Resources.Mass_element;
                return null;
            }
        }
        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddIntegerParameter("Node index", "Node Index", "Index of the node on wich the mass is applied.", GH_ParamAccess.list);
            pManager.AddNumberParameter("Mass", "M (kg)", "Value representing the mass in kg applied on the corresponding node index.", GH_ParamAccess.list);
        
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Point mass", "Point Mass (kg/node)", "Dynamic Mass applied on a node.", GH_ParamAccess.list);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {

            int ind = -1;

            //Get the inputs
            List<int> PointIndex = new List<int>();
            if (!DA.GetDataList(0, PointIndex)) { return; }


            List<double> mass = new List<double>(); //Value of the mass
            if (!DA.GetDataList(1, mass)) { return; }


            List<GH_PointMass> Return = new List<GH_PointMass>();

            if (mass.Count != PointIndex.Count) //Verify the length of the inputed lists
            {
                DA.SetData(0, null);
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Please check the input length.");
            }
            else
            {
                for (int i = 0; i < mass.Count; i++)//For each element, create a  GH PointMass element who is used for the dynamic computation as "point mass" 
                {
                    Vector3d vector = new Vector3d();
                    vector.Z = mass[i]; //Only the z direction has a value
                    Return.Add(new GH_PointMass(new PointMass(PointIndex[i], vector))); //Add the elements to the list of GH point load element that will be returned
                }
            }
            
            //return the list 
            DA.SetDataList(0, Return);
        }

        #endregion Methods
    }
}