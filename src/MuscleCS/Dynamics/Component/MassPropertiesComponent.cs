using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Grasshopper.Kernel;
using Rhino.Geometry;


namespace Muscle.Dynamics
{
        public class MassPropertiesComponent : GH_Component
        {
            public MassPropertiesComponent() :
                base("Point Mass Properties", "Mass Prop", "Get the properties of one or more point mass(es).", "Muscles", "Dynamics")
            {
            }

            public override Guid ComponentGuid { get { return new Guid("d1c67c01-cfa2-4b09-a1bf-2e33a4272aea"); } }

            protected override System.Drawing.Bitmap Icon
            {
                get
                {
                    //return Properties.Resources.MassDisplay;
                    return null;
                }
            }


        protected override void RegisterInputParams(GH_InputParamManager pManager)
            {
                pManager.AddGenericParameter("Point Mass", "Point Mass (kg/node)", "Point mass who is used for the dynamic computation.", GH_ParamAccess.item);
            }

            protected override void RegisterOutputParams(GH_OutputParamManager pManager)
            {
                pManager.AddIntegerParameter("Node index", "Node Index", "Index of the node(s) on wich the point masses are applied. This list is sorted in the same way than the one of the output 'Mass' of this component.", GH_ParamAccess.item);
                pManager.AddNumberParameter("Mass", "M (kg/node)", "Mass in kg applied on the node.", GH_ParamAccess.item);
            }

            protected override void SolveInstance(IGH_DataAccess DA)
            {
                GH_PointMass ghPointMass = new GH_PointMass();
                
                //Obtain the data
                if (!DA.GetData(0, ref ghPointMass)) { return; }

                //Return the data linked to the point masses put as input 
                DA.SetData(0, ghPointMass.Value.NodeInd);
                DA.SetData(1, ghPointMass.Value.Vector.Z);
            }
        }
    }

