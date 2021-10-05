using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles.Nodes
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
            pManager.AddPointParameter("Point", "Pt", "The node coordinates (m)", GH_ParamAccess.item); //0
            pManager.AddIntegerParameter("Fixations Count", "n Fix", "number of fixed translations", GH_ParamAccess.item);//1)
            pManager.AddBooleanParameter("Is Free", "Is Free", "Is it free to move in [X, Y, Z] directions ?", GH_ParamAccess.list); //2
            pManager.AddVectorParameter("Load Additional", "L (kN)", "Additional Loads applied on the structure", GH_ParamAccess.item); //3
            pManager.AddVectorParameter("Load Total", "L tot (kN)", "Total Loads applied on the structure", GH_ParamAccess.item); //4
            pManager.AddVectorParameter("Displacement Additionnal", "d (m)", "Additional Displacement coming only from the additional loads", GH_ParamAccess.item); //5
            pManager.AddVectorParameter("Displacement Total", "d tot (m)", "Total Displacement coming from all applied loads", GH_ParamAccess.item); //6
            pManager.AddVectorParameter("Reaction Additional", "R (kN)", "Additional Reactions coming only from the additional loads", GH_ParamAccess.item); //7
            pManager.AddVectorParameter("Reaction Total", "R tot (kN)", "Total Reactions coming from all applied loads", GH_ParamAccess.item); //8
            //pManager.AddBooleanParameter("IsValid", "IsValid", "True", GH_ParamAccess.item); //9
        }

        /// <summary>
        /// This is the method that actually does the work.
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

            int final = n.Load_Results.Count - 1;
            if (final >=0)
            {
                DA.SetData(3, n.Load_Results[final]/1e3);
                DA.SetData(4, n.Load_Total[final]/1e3);
                DA.SetData(5, n.Displacement_Results[final]);
                DA.SetData(6, n.Displacement_Total[final]);
                DA.SetData(7, n.Reaction_Results[final] / 1e3);
                DA.SetData(8, n.Reaction_Total[final] / 1e3);
            }
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
            get { return new Guid("bcf4cc47-a960-481c-be53-055fcd8ba1af"); }
        }
    }
}