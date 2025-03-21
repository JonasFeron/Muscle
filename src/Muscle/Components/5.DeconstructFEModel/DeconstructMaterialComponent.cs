using Grasshopper.Kernel;
using MuscleApp.ViewModel;
using System;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.DeconstructFEModel
{

    public class DeconstructMaterialComponent : GH_Component
    {

        #region Properties



        #endregion Properties

        #region Constructors

        /// <summary>
        /// Get the mechanical properties of a material.
        /// </summary>
        public DeconstructMaterialComponent() : base("Deconstruct Material", "DeMat", "Deconstruct a bilinear material to retrieve its properties.", GHAssemblyName, Folder5_DeconstructFEM) { }


        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("fdfb5faf-64ac-436b-ab95-f437685aadc1"); } }
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
            pManager.AddIntervalParameter("Yield strengths", "Fy (MPa)", "Linear elastic domain of the material [Compressive Yield Strength, Tensile Yield Strength] in MPa.", GH_ParamAccess.item);

            // Registration of the young modulus input
            pManager.AddNumberParameter("Compressive Young modulus", "Ec (MPa)", "Compressive Young modulus of the material in MPa.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Tensile Young modulus", "Et (MPa)", "Tensile Young modulus of the material in MPa.", GH_ParamAccess.item);

            // Registration of the density input
            pManager.AddNumberParameter("Specific Mass", "\u03c1 (kg/m3)", "Density of the material in kg/m^3.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            BilinearMaterial material = null;

            if (!DA.GetData(0, ref material)) { return; }

            var LinearElasticDomain = new Interval(material.Fyc * 1e-6, material.Fyt * 1e-6);

            DA.SetData(0, material.Name);
            DA.SetData(1, LinearElasticDomain);
            DA.SetData(2, material.Ec * 1e-6);
            DA.SetData(3, material.Et * 1e-6);
            DA.SetData(4, material.Rho);
        }

        #endregion Methods

    }
}