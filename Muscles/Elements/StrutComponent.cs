using Grasshopper.Kernel;
using Muscles.CrossSections;
using Muscles.Materials;
using Rhino.Geometry;
using System;
using System.Windows.Forms;

namespace Muscles.Elements
{
    public class StrutComponent : GH_Component
    {
        public bool displayIn3d { get; set; }
        public StrutComponent() : base("Element - Strut", "E", "A Strut is a linear elastic structural element working only in compression. a Strut may or may not be sensitive to buckling.", "Muscles", "Elements") { displayIn3d = true; }
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("aa41f9f1-07f7-4d8d-8db8-6c4aead45bd4"); } }

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
            pManager.AddLineParameter("Line", "L", "Line defining the strut element.", GH_ParamAccess.item);
            pManager.HideParameter(0);
            pManager.AddGenericParameter("Cross section", "CS", "Cross section of the strut element.", GH_ParamAccess.item);
            pManager[1].Optional = true;
            pManager.AddGenericParameter("Material", "M", "Material of the strut element.", GH_ParamAccess.item);
            pManager[2].Optional = true;
            pManager.AddTextParameter("Buckling Law", "Buckl law", "Choose a buckling law between \"Euler\", \"Rankine\", Eurocode (EN1993) curves \"a\",\"b\",\"c\",\"d\". \nNote that yielding law will apply if the inputted text does not exactly match any of the \"suggestions\".", GH_ParamAccess.item, "Not Applicable");
            pManager[3].Optional = true;
            pManager.AddNumberParameter("Buckling Factor", "k", "Buckling factor k defines the buckling length Lb such that Lb = k*L", GH_ParamAccess.item, 1.0);
            pManager[4].Optional = true;
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Element - Strut", "E", "A strut element", GH_ParamAccess.item);
        }



        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Line line = new Line();
            GH_CrossSection ghCS_Comp = new GH_CrossSection();
            GH_Muscles_Material ghMat_Comp = new GH_Muscles_Material();
            string law = " ";
            double k = 1.0;


            if (!DA.GetData(0, ref line)) { return; }
            if (!DA.GetData(1, ref ghCS_Comp)) { }
            if (!DA.GetData(2, ref ghMat_Comp)) { }
            if (!DA.GetData(3, ref law)) { }
            if (!DA.GetData(4, ref k)) { }


            Strut e = new Strut(line, ghCS_Comp.Value, ghMat_Comp.Value, law, k);
            GH_Element gh_e = new GH_Element(e);

            DA.SetData(0, gh_e);
        }

        #endregion Methods
    }
}
