using Grasshopper.Kernel;
using Muscle.View;
using MuscleApp.ViewModel;
using System;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.ConstructFEModel
{
    /// <summary>
    /// Component that allows to create custom material.
    /// </summary>
    public class MaterialTensionOnlyComponent : GH_Component
    {


        #region Constructors

        /// <summary>
        /// This is the MaterialComponent Constructor. It uses base constructor to set name, nickname, description, category and subcategory of the component.
        /// </summary>
        public MaterialTensionOnlyComponent() : base("Material - Tension Only", "M", "Define a material with linear properties in tension, and null stiffness and strength in compression.", GHAssemblyName, Folder2_ConstructFEM) { }

        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("9739ff11-84ba-48d2-8e72-b5dc0c078b82"); } }

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
            pManager.AddTextParameter("Name", "N", "Name of the material.", GH_ParamAccess.item, "Material");

            // Registration of the young modulus input
            pManager.AddNumberParameter("Young modulus", "E (MPa)", "Tensile Young modulus of the material in MPa. The compressive Young modulus is set to 0.", GH_ParamAccess.item, 0.0);

            // Registration of the yield strength input
            pManager.AddNumberParameter("Yield strength", "Fy (MPa)", "Tensile yield strength of the material in MPa. The compressive yield strength is set to 0.", GH_ParamAccess.item, 0.0);

            // Registration of the density input
            pManager.AddNumberParameter("Specific mass", "\u03c1 (kg/m3)", "Density of the material in kg/m^3.", GH_ParamAccess.item, 0.0);
            pManager[0].Optional = true;
            pManager[1].Optional = true;
            pManager[2].Optional = true;
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
            double youngT = 0.0; //value in MPa
            double fy = 0.0; //value in MPa
            double rho = 0.0; //value in kg/m3

            if (!DA.GetData(0, ref name)) { }
            if (!DA.GetData(1, ref youngT)) { }
            if (!DA.GetData(2, ref fy)) { }
            if (!DA.GetData(3, ref rho)) { }

            //process data

            var material = new BilinearMaterial(name, 0.0, youngT * 1e6, new Interval(0.0, fy * 1e6), rho); // E and fy are saved in Pa in the material object
            GH_BilinearMaterial gh_material = new GH_BilinearMaterial(material); // material is wrapped in a GH_material which can be interpreted by grasshopper

            // check data validity
            if (!gh_material.IsValid)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, gh_material.IsValidWhyNot);
                return;
            }

            // Set output value 
            DA.SetData(0, gh_material); //GH_material is sent to GH 
        }

        #endregion Methods

    }
}