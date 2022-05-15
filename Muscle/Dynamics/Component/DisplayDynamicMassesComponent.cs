using System;
using System.Collections;
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
using Rhino;
using Rhino.Geometry;
using Rhino.Geometry.Collections;
using Rhino.Display;
using System.Drawing;

namespace Muscle.Dynamics
{
    public class DisplayDynamicMassesComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DisplayDynamicMassesComponent()
          : base("Display Dynamic Masses", "DMD",
                "Display the dynamic masses contained in the structure. (This component need to be connected directly to the 'Sphere' component of Grasshopper.)", "Muscles", "Dynamics")
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
            get { return new Guid("1b8cdcf3-c5fa-4722-a48d-d3b33166c040"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may already be subjected to some loads or prestress from previous calculations.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Scale", "Scale", "Scaling of the display of the masses", GH_ParamAccess.item);
            //pManager.AddGenericParameter("Node", "N", "A structural node.", GH_ParamAccess.item); //0

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddPointParameter("Point", "Pt (m)", "The current node coordinates.", GH_ParamAccess.list); //0
            pManager.AddNumberParameter("Radius", "R", "Radius of the sphere following the masses", GH_ParamAccess.list);

        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            log.Info("Dynamic computation: NEW SOLVE INSTANCE");



            StructureObj structure = new StructureObj();
            //Node n = new Node();
            int scale = new int();
            List<Point3d> point = new List<Point3d>();
            List<double> listDynMasses = new List<double>();
            List<double> listScale = new List<double>();
            

            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetData(1, ref scale)) { return; }
            
            listDynMasses = structure.DynMass;
            
            double MaxMass = Enumerable.Max(listDynMasses); 
            double MinMass = Enumerable.Min(listDynMasses);

            double MinScale = AccessToAll.DisplaySupportAmpli;
            double MaxScale = Convert.ToDouble(scale*2)*AccessToAll.DisplaySupportAmpli;

            if(MinScale == MaxScale)
            {
                MaxScale = Convert.ToDouble(2) * MinScale;
            }


            for (int i = 0; i < listDynMasses.Count; i++)
            {

                Node node = structure.StructuralNodes[i];
                Point3d PointToUse = node.Point;
                point.Add(PointToUse);

                if (MinMass == MaxMass)
                {
                    double ScaleToAdd = MaxScale;
                    listScale.Add(ScaleToAdd);
                }
                else
                {
                    double MassToUse = listDynMasses[i];
                    double ScaleToAdd = MinScale + (MassToUse-MinMass)/(MaxMass-MinMass)*(MaxScale-MinScale);
                    listScale.Add(ScaleToAdd);
                }
                
            }
            


            DA.SetDataList(0, point);
            DA.SetDataList(1, listScale);



            log.Info("Dynamic computation: END SOLVE INSTANCE");
        }
    
    }
}