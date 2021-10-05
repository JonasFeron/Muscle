using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles.Structure
{
    public class DisassembleStructureComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DisassembleStructureComponent()
          : base("Structure - Disassemble", "Disassemble",
              "Get the nodes and elements objects composing the structure",
              "Muscles", "Model")
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "Struct", "A Structure is made of Nodes and Elements", GH_ParamAccess.item); //0
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Nodes", "N", "The structural nodes.", GH_ParamAccess.list); //0
            pManager.AddGenericParameter("Elements", "E", "The finite elements composing the structure.", GH_ParamAccess.list); //1
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            StructureObj structure = new StructureObj();

            if (!DA.GetData(0, ref structure)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetDataList(0, structure.Struct_Nodes);
            DA.SetDataList(1, structure.Struct_Elements);
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
            get { return new Guid("928c1595-ef2e-4f5b-a6ed-8f5283e83420"); }
        }
    }
}