using System;
using System.Collections.Generic;
using System.IO;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.Elements;
using Muscle.PythonLink;
using Muscle.PythonLink.Component;
using Newtonsoft.Json;
using Rhino.Geometry;

// In order to load the result of this wizard, you will also need to
// add the output bin/ folder of this project to the list of loaded
// folder in Grasshopper.
// You can use the _GrasshopperDeveloperSettings Rhino command for that.

namespace Muscle.Structure
{
    public class AssembleStructureComponent : GH_Component
    {

        #region Properties
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);


        #endregion Properties
        #region Constructors

        /// <summary>
        /// Creation of the Component on the GH Canvas
        /// </summary>
        public AssembleStructureComponent()
          : base("Structure - Assemble", //Name
                "Structure", //NickName
              "Creates a Finite Element Model (FEM) of the Structure.",//Description
              "Muscles", "Model")
        {

        }

        /// <summary>
        /// Each component must have a unique Guid to identify it. 
        /// It is vital this Guid doesn't change otherwise old gh files that use the old ID will partially fail during loading.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("a9ca4b75-9812-4df4-9d9e-dc176afa61f4"); }
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
            pManager.AddGenericParameter("Elements", "E", "The finite elements.", GH_ParamAccess.tree);
            pManager.AddPointParameter("(Points)", "(Pt)", "(Optional) If no points are inputted, the points are extracted from the elements extremities in a random order", GH_ParamAccess.tree, null);
            pManager.AddGenericParameter("(Supports)", "(Spt)", "(Optional) Define the supports of the structure. A Structure may be self-stressed but can not be loaded without supports.", GH_ParamAccess.tree);
            pManager[1].Optional = true;
            pManager[2].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "Struct", "A Structure is made of Points, Elements, (Supports)", GH_ParamAccess.item); //0
        }

        #endregion Constructors




        #region Methods

        /// <summary>
        /// This is the method that actually does the main work of the component.
        /// </summary>
        /// <param name="DA">The DA object can be used to retrieve data from input parameters and to store data in output parameters.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            log.Info("Main ASSEMBLE: NEW SOLVE INSTANCE");

            // 1) Collect Inputs
            GH_Structure<IGH_Goo> gh_elements_input = new GH_Structure<IGH_Goo>();
            GH_Structure<GH_Point> points_input = new GH_Structure<GH_Point>();
            GH_Structure<IGH_Goo> supports_input = new GH_Structure<IGH_Goo>();

            if (!DA.GetDataTree(0, out gh_elements_input)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.
            if (!DA.GetDataTree(1, out points_input)) { } // Nothing happen if i can't collect points.
            if (!DA.GetDataTree(2, out supports_input)) { supports_input = null; }  //no default value can be inputted for a generic parameter

            // 2) Create and solve geometry object 
            StructureObj structure = null;
            try
            {
                structure = new StructureObj(gh_elements_input, points_input, supports_input); // A geometry object is created from lines, points and supports. The validity of the inputs are checked when constructing the object.
            }
            catch (InvalidDataException e) // error if the supports inputted by the user are not real supports
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                return;
            }
            foreach (string warning in structure.warnings) //warnings if some user inputs are weird but the application can still run
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, warning);
            }

            GH_StructureObj gh_structure = new GH_StructureObj(structure);

            // 3) Set outputs
            DA.SetData(0, gh_structure);

            log.Info("Main ASSEMBLE: END SOLVE INSTANCE");
        }

        #endregion Methods


    }
}

