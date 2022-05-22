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
                base("Point mass properties", "Mass Prop", "Get the properties of a point mass", "Muscles", "Dynamics")
            {
            }

            public override Guid ComponentGuid { get { return new Guid("d1c67c01-cfa2-4b09-a1bf-2e33a4272aea"); } }

            protected override void RegisterInputParams(GH_InputParamManager pManager)
            {
                pManager.AddGenericParameter("Point Mass", "Mass (kg)", "Mass", GH_ParamAccess.item);
            }

            protected override void RegisterOutputParams(GH_OutputParamManager pManager)
            {
                pManager.AddIntegerParameter("Node", "N", "Node of application of the mass.", GH_ParamAccess.item);
                pManager.AddNumberParameter("Vector", "V (kg)", "Vector representing the mass in kg.", GH_ParamAccess.item);
            }

            protected override void SolveInstance(IGH_DataAccess DA)
            {
                GH_PointLoad ghPointLoad = new GH_PointLoad();

                if (!DA.GetData(0, ref ghPointLoad)) { return; }


                DA.SetData(0, ghPointLoad.Value.NodeInd);
                DA.SetData(1, ghPointLoad.Value.Vector.Z);
            }
        }
    }

