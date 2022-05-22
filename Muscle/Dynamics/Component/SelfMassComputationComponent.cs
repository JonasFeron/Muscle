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
using Muscle.Structure;
using Rhino.Geometry;


namespace Muscle.Dynamics
{
    public class SelfMassComputationComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public SelfMassComputationComponent()
          : base("Display Dynamic Masses/Loads", "DMD",
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
            get { return new Guid("b50368a9-292e-4a65-8dc5-18ca0d3f60ef"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Elements", "E", "Generate self-weight loads applied on the extrimities of the given elements.", GH_ParamAccess.item);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Self-mass", "Self mass (kg)", "", GH_ParamAccess.list);
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

            double MaxMass = Math.Round(Enumerable.Max(listDynMasses), 1);
            double MinMass = Math.Round(Enumerable.Min(listDynMasses), 1);

            if (scale == 0) //Security
            {
                scale = 1;
            }

            if (AccessToAll.DisplayDyn == 0) //Security
            {
                AccessToAll.DisplayDyn = 0.05;
            }


            double MinScale = AccessToAll.DisplayDyn;
            double MaxScale = Convert.ToDouble(scale) * AccessToAll.DisplayDyn;

            if (MinScale == MaxScale)
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
                    double MassToUse = Math.Round(listDynMasses[i], 1);
                    double ScaleToAdd = MinScale + (MassToUse - MinMass) / (MaxMass - MinMass) * (MaxScale - MinScale);
                    listScale.Add(ScaleToAdd);
                }

            }





            DA.SetDataList(0, point);
            DA.SetDataList(1, listScale);



            log.Info("Dynamic computation: END SOLVE INSTANCE");
        }

    }

}
