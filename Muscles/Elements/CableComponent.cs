using Grasshopper.Kernel;
using Muscles.CrossSections;
using Muscles.Materials;
using Rhino.Geometry;
using System;
using System.Windows.Forms;

namespace Muscles.Elements
{
    public class CableComponent : GH_Component
    {
        public bool displayIn3d { get; set; }
        public CableComponent() : base("Element - Cable", "C", "A Cable is a linear elastic structural element working only in tension.", "Muscles", "Elements") { displayIn3d = true; }
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("cbd17050-3042-4adb-bf25-e3ba54ed49fb"); } }

        public override void AppendAdditionalMenuItems(ToolStripDropDown menu)
        {
            base.AppendAdditionalMenuItems(menu);
        }

        public override bool AppendMenuItems(ToolStripDropDown menu)
        {
            //Menu_AppendItem(menu, "Display in 3D", displayClick, true, displayIn3d);
            //Menu_AppendItem(menu, "Display as line", displayClick, true, !displayIn3d);
            //Menu_AppendSeparator(menu);
            return base.AppendMenuItems(menu);
        }

        public void displayClick(object sender, EventArgs e)
        {
            displayIn3d = !displayIn3d;
        }

        protected override void AppendAdditionalComponentMenuItems(ToolStripDropDown menu)
        {
            base.AppendAdditionalComponentMenuItems(menu);
        }

        #endregion Properties

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddLineParameter("Line", "L", "Line defining the cable element", GH_ParamAccess.item);
            pManager.HideParameter(0);
            pManager.AddGenericParameter("Cross section", "CS", "Cross section of the cable element", GH_ParamAccess.item);
            pManager[1].Optional = true;
            pManager.AddGenericParameter("Material", "M", "Material of the cable element", GH_ParamAccess.item);
            pManager[2].Optional = true;
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Element - Cable", "E", "A cable element", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Line line = new Line();
            GH_CrossSection ghCS_Tens = new GH_CrossSection();
            GH_Muscles_Material ghMat_Tens = new GH_Muscles_Material();

            if (!DA.GetData(0, ref line)) { return; }
            if (!DA.GetData(1, ref ghCS_Tens)) { }
            if (!DA.GetData(2, ref ghMat_Tens)) {  }

            Cable e = new Cable(line,ghCS_Tens.Value,ghMat_Tens.Value);
            GH_Element gh_e = new GH_Element(e);

            DA.SetData(0, gh_e);
        }

        #endregion Methods
    }
}
