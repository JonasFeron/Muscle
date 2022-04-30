using Grasshopper.Kernel;
using System;

namespace Muscle.Materials
{

    public class MaterialPropertiesComponent : GH_Component
    {

        #region Properties



        #endregion Properties

        #region Constructors

        /// <summary>
        /// Get the mechanical properties of a material.
        /// </summary>
        public MaterialPropertiesComponent() : base("Material Properties", "Prop", "Get the mechanical properties of a material.", "Muscles", "Elements") { }


        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("e5ec3942-c8fa-4349-9597-cfbb2aa2d7c8"); } }
        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            // Registration of the material input
            pManager.AddGenericParameter("Material", "M", "Material", GH_ParamAccess.item);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            // Registration of the material name input
            pManager.AddTextParameter("Name", "N", "Name of the material.", GH_ParamAccess.item);

            // Registration of the yield strength input
            pManager.AddNumberParameter("Yield strength", "Fy (MPa)", "Yield Strength of the material in MPa.", GH_ParamAccess.item);

            // Registration of the young modulus input
            pManager.AddNumberParameter("Young modulus", "E (MPa)", "Young modulus of the material in MPa.", GH_ParamAccess.item);

            // Registration of the density input
            pManager.AddNumberParameter("Specific Mass", "\u03c1 (kg/m3)", "Density of the material in kg/m^3.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Muscles_Material material = null;

            if (!DA.GetData(0, ref material)) { return; }

            DA.SetData(0, material.Name);
            DA.SetData(1, material.Fy * 1e-6);
            DA.SetData(2, material.E * 1e-6);
            DA.SetData(3, material.Rho);
        }

        #endregion Methods

    }
}