using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscle.Nodes
{
    public class NodePropertiesComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public NodePropertiesComponent()
          : base("Node Properties", "Node prop",
              "Get the properties of nodes.",
              "Muscles", "Model")
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Node", "N", "A structural node.", GH_ParamAccess.item); //0
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddPointParameter("Point", "Pt (m)", "The current node coordinates.", GH_ParamAccess.item); //0
            pManager.AddIntegerParameter("Fixations Count", "n Fix", "number of fixed translations.", GH_ParamAccess.item);//1)
            pManager.AddBooleanParameter("Is Free", "Is Free", "Is it free to move in [X, Y, Z] directions ?", GH_ParamAccess.list); //2
            pManager.AddVectorParameter("Load", "Load (kN)", "Sum of all loads applied on each node.", GH_ParamAccess.item); //3
            pManager.AddVectorParameter("Unbalanced Load", "Res (kN)", "The residual loads that are not in equilibrium with the internal axial forces.", GH_ParamAccess.item); //4
            pManager.AddVectorParameter("Reactions", "React (kN)", "Reaction forces of the supports.", GH_ParamAccess.item); //5
            //pManager.AddBooleanParameter("IsValid", "IsValid", "True", GH_ParamAccess.item); //9
        }

        /// <summary>
        ///
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Node n = new Node();

            if (!DA.GetData(0, ref n)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetData(0, n.Point);
            DA.SetData(1, n.FixationsCount);

            List<bool> IsFree = new List<bool> { n.isXFree, n.isYFree, n.isZFree };
            DA.SetDataList(2, IsFree);
            DA.SetData(3, n.Load / 1000);
            DA.SetData(4, n.Residual / 1000);
            DA.SetData(5, n.Reaction / 1000);
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
            get { return new Guid("27077155-791f-4f85-95de-6e44c70734ee"); }
        }
    }
}