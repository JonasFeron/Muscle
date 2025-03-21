using System;
using System.Collections.Generic;
using Grasshopper.Kernel;
using MuscleApp.ViewModel;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.DeconstructFEModel
{
    public class DeconstructNodeComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DeconstructNodeComponent()
          : base("Deconstruct Node", "DeNode",
              "Deconstruct a node to retrieve its properties.",
              GHAssemblyName, Folder5_DeconstructFEM)
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Node", "N", "Input node", GH_ParamAccess.item); //0
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddPointParameter("Point", "Pt (m)", "Current node coordinates", GH_ParamAccess.item); //0
            pManager.AddIntegerParameter("Index", "Idx", "Node index", GH_ParamAccess.item);//1)
            pManager.AddBooleanParameter("Is Free", "DoF", "Is it free to move in [X, Y, Z] directions ? Degrees of Freedom are: True if free, False if fixed by a support.", GH_ParamAccess.list); //2
            pManager.AddVectorParameter("Load", "L (kN)", "Total loads applied on the node", GH_ParamAccess.item); //3
            pManager.AddVectorParameter("Unbalanced Load", "U (kN)", "Unbalanced loads or residuals from the equilibrium with the internal axial forces", GH_ParamAccess.item); //4
            pManager.AddVectorParameter("Reactions", "R (kN)", "Reaction forces at the supports", GH_ParamAccess.item); //5
        }

        /// <summary>
        ///
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Node n = new Node();

            if (!DA.GetData(0, ref n)) { return; } 

            DA.SetData(0, n.Coordinates);
            DA.SetData(1, n.Idx);
            List<bool> IsFree = new List<bool> { n.isXFree, n.isYFree, n.isZFree };
            DA.SetDataList(2, IsFree);
            DA.SetData(3, n.Loads / 1000);
            DA.SetData(4, n.Residuals / 1000);
            DA.SetData(5, n.Reactions / 1000);
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
            get { return new Guid("fdfb5faf-64ac-436b-ab95-f437685aadc1"); }
        }
    }
}