using System;
using System.Collections.Generic;
using System.IO;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscles.Elements;
using Muscles.PythonLink;
using Muscles.PythonLink.Component;
using Newtonsoft.Json;
using Rhino.Geometry;

// In order to load the result of this wizard, you will also need to
// add the output bin/ folder of this project to the list of loaded
// folder in Grasshopper.
// You can use the _GrasshopperDeveloperSettings Rhino command for that.

namespace Muscles.Structure
{
    public class DeformedStructureComponent : GH_Component
    {

        #region Constructors
                
        /// <summary>
        /// Creation of the Component on the GH Canvas
        /// </summary>
        public DeformedStructureComponent()
          : base("Structure - Deformed", //Name
                "Deformed", //NickName
              "return a deformed structure",//Description
              "Muscles", "Results")
        {
        }

        /// <summary>
        /// Each component must have a unique Guid to identify it. 
        /// It is vital this Guid doesn't change otherwise old gh files that use the old ID will partially fail during loading.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("e6e2a7b4-7688-45e7-9ade-024d7299a56c"); }
        }

        /// <summary>
        /// Provides an Icon for every component that will be visible in the User Interface.
        /// Icons need to be 24x24 pixels.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                // You can add image files to your project resources and access them like this:
                //return Resources.IconForThisComponent;
                return null;
            }
        }


        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            // all inputs are GH_ParamAccess.tree. because we create only 1 geometry, no matter how many branches have the trees. (list access would create 1 geometry per branch) 
            pManager.AddGenericParameter("Solved Structrure", "Struct", "A previously solved structure", GH_ParamAccess.item);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Deformed Structure", "Struct", "The deformed shape of the structure", GH_ParamAccess.item); //0
        }

        #endregion Constructors

        #region Properties


        #endregion Properties

        
        #region Methods

        /// <summary>
        /// This is the method that actually does the main work of the component.
        /// </summary>
        /// <param name="DA">The DA object can be used to retrieve data from input parameters and to store data in output parameters.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {

            // 1) Collect Inputs
            StructureObj structure = new StructureObj();

            if (!DA.GetData(0, ref structure)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetData(0, structure.Deformed());
        }


        #endregion Methods


    }
}
