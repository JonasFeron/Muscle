using System;
using System.IO;
using System.Collections.Generic;
using Rhino.Geometry;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.View;
using MuscleApp.ViewModel;
using Muscle.Converters;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.ConstructFEModel
{
    public class ConstructStructureComponent : GH_Component
    {

        #region Properties


        #endregion Properties
        #region Constructors

        /// <summary>
        /// Creation of the Component on the GH Canvas
        /// </summary>
        public ConstructStructureComponent()
          : base("Construct Structure", //Name
                "Structure", //NickName
              "Creates a Finite Element Model (FEM) of the Structure.",//Description
              GHAssemblyName, Folder2_ConstructFEM)
        {

        }

        /// <summary>
        /// Each component must have a unique Guid to identify it. 
        /// It is vital this Guid doesn't change otherwise old gh files that use the old ID will partially fail during loading.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("5c5fcced-06a7-42ce-ba8d-ed9884722981"); }
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
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            // all inputs are GH_ParamAccess.tree. because we create only 1 geometry, no matter how many branches have the trees. (list access would create 1 geometry per branch) 
            pManager.AddGenericParameter("Elements", "E", "The finite elements.", GH_ParamAccess.tree);
            pManager.AddPointParameter("(Points)", "(Pt)", "(Optional) If no points are provided, the points are extracted from the elements ends in a random order", GH_ParamAccess.tree, null);
            pManager.AddGenericParameter("(Supports)", "(Spt)", "(Optional) Define the supports of the structure. A Structure may be self-stressed but can not be loaded without supports.", GH_ParamAccess.tree);
            pManager[1].Optional = true;
            pManager[2].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
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

            // 1) Collect Inputs
            GH_Structure<IGH_Goo> gh_elements = new GH_Structure<IGH_Goo>();
            GH_Structure<GH_Point> gh_points = new GH_Structure<GH_Point>();
            GH_Structure<IGH_Goo> gh_supports = new GH_Structure<IGH_Goo>();

            if (!DA.GetDataTree(0, out gh_elements)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.
            if (!DA.GetDataTree(1, out gh_points)) { } // Nothing happen if i can't collect points.
            if (!DA.GetDataTree(2, out gh_supports)) { gh_supports = null; }  //no default value can be inputted for a generic parameter

            // Convert Grasshopper data to MuscleApp ViewModel types
            List<Element> elements = GH_Decoders.ToElementList(gh_elements);
            List<Point3d> points = GH_Decoders.ToPoint3dList(gh_points);
            List<Support> supports = GH_Decoders.ToSupportList(gh_supports);

            // 2) Create and solve geometry object 
            Truss structure = null;
            try
            {
                structure = new Truss(elements, points, supports); // A geometry object is created from lines, points and supports. The validity of the inputs are checked when constructing the object.
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

            // 3) Set outputs 
            DA.SetData(0, new GH_Truss(structure));

        }

        #endregion Methods


    }
}

