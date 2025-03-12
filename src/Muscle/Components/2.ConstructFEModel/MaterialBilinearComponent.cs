using Grasshopper.Kernel;
using Muscle.GHModel;
using Muscle.ViewModel;
using System;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.ConstructFEModel
{
    /// <summary>
    /// Component that allows to create custom material.
    /// </summary>
    public class MaterialBilinearComponent : GH_Component
    {


        #region Constructors

        /// <summary>
        /// This is the MaterialComponent Constructor. It uses base constructor to set name, nickname, description, category and subcategory of the component.
        /// </summary>
        public MaterialBilinearComponent() : base("Bilinear Material", "M", "Define a material with bilinear properties", GHAssemblyName, Folder2_ConstructFEM) { }

        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("84b730f1-3a39-4d2b-9526-2dc8955dd7bf"); } }

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
            pManager.AddNumberParameter("Compressive Young modulus", "Ec (MPa)", "Compressive Young modulus of the material in MPa.", GH_ParamAccess.item, 0.0);
            pManager.AddNumberParameter("Tensile Young modulus", "Et (MPa)", "Tensile Young modulus of the material in MPa.", GH_ParamAccess.item, 0.0);

            // Registration of the yield strength input
            pManager.AddIntervalParameter("Yield strengths", "Fy (MPa)", "Linear elastic domain of the material [Compressive Yield Strength, Tensile Yield Strength] in MPa. Note: Compression is negative.", GH_ParamAccess.item, new Interval(double.NegativeInfinity, double.PositiveInfinity));

            // Registration of the density input
            pManager.AddNumberParameter("Specific mass", "\u03c1 (kg/m3)", "Density of the material in kg/m^3.", GH_ParamAccess.item, 0.0);
            pManager[0].Optional = true;
            pManager[1].Optional = true;
            pManager[2].Optional = true;
            pManager[3].Optional = true;
            pManager[4].Optional = true;
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
            double youngC = 0.0; //value in MPa
            Interval fy = new Interval(double.NegativeInfinity, double.PositiveInfinity); //value in MPa
            double rho = 0.0; //value in kg/m3

            if (!DA.GetData(0, ref name)) { }
            if (!DA.GetData(1, ref youngC)) { }
            if (!DA.GetData(2, ref youngT)) { }
            if (!DA.GetData(3, ref fy)) { }
            if (!DA.GetData(4, ref rho)) { }

            //process data

            var material = new BilinearMaterial(name, youngC * 1e6, youngT * 1e6, new Interval(fy.T0 *1e6, fy.T1 *1e6), rho); // E and fy are saved in Pa in the material object
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