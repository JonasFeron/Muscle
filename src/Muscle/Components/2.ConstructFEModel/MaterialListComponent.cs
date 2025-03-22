using Grasshopper.Kernel;
using System;
using System.Windows.Forms;
using Muscle.View;
using MuscleApp.ViewModel;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.CreateModel
{
    /// <summary>
    /// Component that provides predefined materials.
    /// </summary>
    public class MaterialListComponent : GH_Component
    {

        #region Fields

        // Currently selected material
        // S235 steel by default
        private string material = "S235";

        #endregion Fields

        #region Properties



        #endregion Properties

        #region Constructors

        /// <summary>
        /// This is the MaterialComponent Constructor. It uses base constructor to set name, nickname, description, category and subcategory of the component.
        /// </summary>
        public MaterialListComponent() : base("Construct Material from list", "M", "Choose one of the multiple default materials via the right click menu.", GHAssemblyName, Folder2_ConstructFEM) { }

        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("c727b5da-b361-4955-bdbb-248f6206f9d4"); } }



        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            // No input
        }


        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Material", "M", "Selected material", GH_ParamAccess.item);
        }

        public override void AppendAdditionalMenuItems(ToolStripDropDown menu)
        {
            base.AppendAdditionalMenuItems(menu);
            Menu_AppendItem(menu, "S235 steel", S235Click, null, true, material == "S235");
            Menu_AppendItem(menu, "S275 steel", S275Click, null, true, material == "S275");
            Menu_AppendItem(menu, "S355 steel", S355Click, null, true, material == "S355");
            Menu_AppendItem(menu, "Aluminum", AluminumClick, null, true, material == "Aluminum");

            // Add menu options for new materials here.
        }
        #endregion Constructors

        #region Methods




        protected override void SolveInstance(IGH_DataAccess DA)
        {
            double Esteel = 210.0 * 1e9; // N/m²
            double fy235 = 235 * 1e6; // N/m²
            double fy355 = 355 * 1e6; // N/m²


            double Ealu = 70.0 * 1e9;
            double fy140 = 140 * 1e6; // N/m²


            switch (material)
            {
                case "S235":
                    DA.SetData(0, new GH_BilinearMaterial(new BilinearMaterial("S235 steel", Esteel, Esteel, new Interval(-fy235, fy235), 7850)));
                    break;

                case "S355":
                    DA.SetData(0, new GH_BilinearMaterial(new BilinearMaterial("S355 steel", Esteel, Esteel, new Interval(-fy355, fy355), 7850)));
                    break;

                case "Aluminium":
                    DA.SetData(0, new GH_BilinearMaterial(new BilinearMaterial("Aluminum", Ealu, Ealu, new Interval(-fy140, fy140), 2700)));
                    break;

                // Add cases for new materials here.

                default:
                    DA.SetData(0, new GH_BilinearMaterial());
                    break;
            }
        }


        /// <summary>
        /// Method called when menu option is clicked. Each method updatethe field "material" to a specific value.
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        public void AluminumClick(object sender, EventArgs e)
        {
            material = "Aluminum";
            ExpireSolution(true); // Force the recomputation of the solution
        }

        public void S235Click(object sender, EventArgs e)
        {
            material = "S235";
            ExpireSolution(true); // Force the recomputation of the solution
        }

        public void S275Click(object sender, EventArgs e)
        {
            material = "S275";
            ExpireSolution(true); // Force the recomputation of the solution
        }

        public void S355Click(object sender, EventArgs e)
        {
            material = "S355";
            ExpireSolution(true); // Force the recomputation of the solution
        }
        // Add click methods for new materials here.

        #endregion Methods


    }
}