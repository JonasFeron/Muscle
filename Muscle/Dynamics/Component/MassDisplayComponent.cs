using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.Elements;
using Muscle.Loads;
using Muscle.Nodes;
using Muscle.PythonLink;
using Muscle.Dynamics;
using Muscle.PythonLink.Component;
using Muscle.Structure;
using Newtonsoft.Json;
using Rhino.Geometry;

namespace Muscle.Dynamics
{
    public class MassDisplayComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public MassDisplayComponent()
          : base("Dynamic Masses Display TEST", "DMDTEST",
                "Display the dynamic masses contained in the structure. (This component need to be connected directly to the 'Sphere' component of Grasshopper.)",
              "Muscles", "Dynamics")
        {
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("e942a7a9-5b7f-4c41-bf91-fe0c15d7199c"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may already be subjected to some loads or prestress from previous calculations.", GH_ParamAccess.item);
         


        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("SelfMass", "SelfMass (kg)", "Point mass due to self-mass. Half of the element's self weight is applied on each of both extremities. ", GH_ParamAccess.list);

        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            
            //1) Collect Data
            StructureObj structure = new StructureObj();
            List<double> DynMassIN = new List<double>(); // Default value
            int NumNode = 0;
            
            //Obtain the data if the component is connected
            if (!DA.GetData(0, ref structure)) { return; }
            NumNode = structure.NodesCount;
            DynMassIN = structure.DynMass;
            List<Node> NodesCoord = structure.StructuralNodes;
            List<GH_PointLoad> selfmass = new List<GH_PointLoad>();
            
            
            for (int i = 0; i < NumNode; i++)
            {
                Vector3d ToAdd = new Vector3d();
                Point3d Coord = new Point3d();
                ToAdd.Z = DynMassIN[i];
                Coord = NodesCoord[i].Point;
                PointLoad Display = new PointLoad();
                Display.Point = Coord;
                Display.Vector = ToAdd;


                
                GH_PointLoad p0 = new GH_PointLoad(new PointLoad( Coord, ToAdd )); //Because the weight is in N
                selfmass.Add(p0);

            }

            DA.SetDataList(0, selfmass);

        }
       
    }
}

