using Grasshopper.Kernel;
using Muscles_ADE.CrossSections;
using Muscles_ADE.Materials;
using Rhino.Geometry;
using System;
using System.Windows.Forms;

namespace Muscles_ADE.Elements
{
    public class CableComponent : GH_Component
    {
        public bool displayIn3d { get; set; }
        public CableComponent() : base("Element - Cable", "C", "A Cable is a linear elastic structural element working only in Tension.\nCompression force can be allowed in the numerical analysis or not.\nIf compression is not allowed, one shall run the analysis non-linearly to consider slacked cables.\nIf compression is allowed for the sake of simplified analysis, the compressed cables will have negative unity check and IsValid==False property.", "Muscles", "Elements") { displayIn3d = true; }
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("701f886a-3aee-4ae1-b1cc-90a824e44cc9"); } }

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
            pManager.AddNumberParameter("Free length", "Free L (m)", "The length of the element free of any strain.\nIf left blank or negative value, the free length will be considered as the length of the inputted Line.", GH_ParamAccess.item, -1.0); //4
            pManager[1].Optional = true;
            pManager.AddGenericParameter("Cross section", "CS", "Cross section of the cable element", GH_ParamAccess.item);
            pManager[2].Optional = true;
            pManager.AddGenericParameter("Material", "M", "Material of the cable element", GH_ParamAccess.item);
            pManager[3].Optional = true;
            pManager.AddBooleanParameter("Can Resist Compression ?", "Allow Comp", "If true, compression will be allowed in the finite element analysis.\nIf false, run a non-linear analysis with 0 forces in slack cables.", GH_ParamAccess.item, true);
            pManager[4].Optional = true;

        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Element - Cable", "E", "A cable element", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Line line = new Line();
            double lFree = -1.0;
            GH_CrossSection ghCS_Tens = new GH_CrossSection();
            GH_Muscles_Material ghMat_Tens = new GH_Muscles_Material();
            bool canResistCompression = true;

            if (!DA.GetData(0, ref line)) { return; }
            if (!DA.GetData(1, ref lFree)) { }
            if (!DA.GetData(2, ref ghCS_Tens)) { }
            if (!DA.GetData(3, ref ghMat_Tens)) { }
            if (!DA.GetData(4, ref canResistCompression)) { }


            Cable e = new Cable(line, lFree, ghCS_Tens.Value, ghMat_Tens.Value, canResistCompression);
            GH_Element gh_e = new GH_Element(e);

            DA.SetData(0, gh_e);
        }

        #endregion Methods
    }
}