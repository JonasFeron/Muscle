using Grasshopper.Kernel;
using System;

namespace Muscle.Materials
{
    /// <summary>
    /// Component that allows to create custom material.
    /// </summary>
    public class MaterialComponent : GH_Component
    {


        #region Constructors

        /// <summary>
        /// This is the MaterialComponent Constructor. It uses base constructor to set name, nickname, description, category and subcategory of the component.
        /// </summary>
        public MaterialComponent() : base("Material", "M", "Define material properties", "Muscles", "Elements") { }

        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("34996462-ee16-409a-9198-3d2399e7c1e6"); } }

        /// <summary>
        /// Property to access component icon.
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
        #endregion Constructors

        #region Methods


        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            // Registration of the material name input
            pManager.AddTextParameter("Name", "N", "Name of the material.", GH_ParamAccess.item);
            pManager[0].Optional = true;

            // Registration of the young modulus input
            pManager.AddNumberParameter("Young modulus", "E (MPa)", "Young modulus of the material in MPa.", GH_ParamAccess.item);

            // Registration of the yield strength input
            pManager.AddNumberParameter("Yield strength", "Fy (MPa)", "Yield Strength of the material in MPa.", GH_ParamAccess.item, 0.0);
            pManager[2].Optional = true;


            // Registration of the density input
            pManager.AddNumberParameter("Specific mass", "\u03c1 (kg/m3)", "Density of the material in kg/m^3.", GH_ParamAccess.item, 0.0);
            pManager[3].Optional = true;
        }


        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            // Registration of the ouput
            pManager.AddGenericParameter("Material", "M", "Material containing physical properties.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // collect datas
            string name = "No Name";
            double young = 0.0; //value in MPa
            double fy = 0.0; //value in MPa
            double rho = 0.0; //value in kg/m3

            if (!DA.GetData(0, ref name)) { }
            if (!DA.GetData(1, ref young)) { return; }
            if (!DA.GetData(2, ref fy)) { }
            if (!DA.GetData(3, ref rho)) { }

            //process data
            Muscles_Material material = new Muscles_Material(name, young * 1e6, fy * 1e6, rho); // E and fy are saved in Pa in the material object
            GH_Muscles_Material gh_material = new GH_Muscles_Material(material); // material is wrapped in a GH_material which can be interpreted by grasshopper

            // Set output value 
            DA.SetData(0, gh_material); //GH_material is sent to GH 
        }

        #endregion Methods

    }
}