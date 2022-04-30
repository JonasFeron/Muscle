using Grasshopper.Kernel;
using Muscle.CrossSections;
using Muscle.Materials;
using Rhino.Geometry;
using System;
using System.Windows.Forms;

namespace Muscle.Elements
{
    public class StrutComponent : GH_Component
    {
        public bool displayIn3d { get; set; }
        public StrutComponent() : base("Element - Strut", "E", "A Strut is a linear elastic structural element working only in compression. a Strut may or may not be sensitive to buckling.", "Muscles", "Elements") { displayIn3d = true; }
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("9de0139f-cf4a-4043-8b1c-25aa726f9dfe"); } }

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
            pManager.AddNumberParameter("Free length", "Free L (m)", "The length of the element free of any strain.\nIf left blank or negative value, the free length will be considered as the length of the inputted Line.", GH_ParamAccess.item, -1.0); //4
            pManager[1].Optional = true;
            pManager.AddGenericParameter("Cross section", "CS", "Cross section of the strut element.", GH_ParamAccess.item);
            pManager[2].Optional = true;
            pManager.AddGenericParameter("Material", "M", "Material of the strut element.", GH_ParamAccess.item);
            pManager[3].Optional = true;
            pManager.AddTextParameter("Buckling Law", "Buckl law", "Choose a buckling law between \"Euler\", \"Rankine\", Eurocode (EN1993) curves \"a\",\"b\",\"c\",\"d\". \nNote that yielding law will apply if the inputted text does not exactly match any of the \"suggestions\".", GH_ParamAccess.item, "Not Applicable");
            pManager[4].Optional = true;
            pManager.AddNumberParameter("Buckling Factor", "k", "Buckling factor k defines the buckling length Lb such that Lb = k*L", GH_ParamAccess.item, 1.0);
            pManager[5].Optional = true;
            pManager.AddBooleanParameter("Can Resist Tension ?", "Allow Tens", "If true, Tension will be allowed in the finite element analysis.\nIf false, run a non-linear analysis with 0 forces in cracked struts.", GH_ParamAccess.item, true);
            pManager[6].Optional = true;

        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Element - Strut", "E", "A strut element", GH_ParamAccess.item);
        }



        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Line line = new Line();
            double lFree = -1;
            GH_CrossSection ghCS_Comp = new GH_CrossSection();
            GH_Muscles_Material ghMat_Comp = new GH_Muscles_Material();
            string law = " ";
            double k = 1.0;
            bool canResistTension = true;


            if (!DA.GetData(0, ref line)) { return; }
            if (!DA.GetData(1, ref lFree)) { }
            if (!DA.GetData(2, ref ghCS_Comp)) { }
            if (!DA.GetData(3, ref ghMat_Comp)) { }
            if (!DA.GetData(4, ref law)) { }
            if (!DA.GetData(5, ref k)) { }
            if (!DA.GetData(6, ref canResistTension)) { }


            Strut e = new Strut(line, lFree, ghCS_Comp.Value, ghMat_Comp.Value, law, k, canResistTension);
            GH_Element gh_e = new GH_Element(e);

            DA.SetData(0, gh_e);
        }

        #endregion Methods
    }
}