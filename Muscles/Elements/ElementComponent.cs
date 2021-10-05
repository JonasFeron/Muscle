using Grasshopper.Kernel;
using Muscles.CrossSections;
using Muscles.Materials;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace Muscles.Elements
{
    public class ElementComponent : GH_Component
    {
        public bool displayIn3d { get; set; }
        public ElementComponent() : base("Element - General", "E", "An Element is the most general (bi-)linear elastic structural element. It allows, for instance, modelling linear reinforced concrete element. In tension, the rebar (A_tens, E_tens) is working. In compression, the concrete (A_comp, E_comp) is working. In compression, the element may or may not be sensitive to buckling. The mass is obtained by considering only the compressive cross-section and material.", "Muscles", "Elements") 
        { 
            displayIn3d = true;
        }

        #region Properties

        public override Guid ComponentGuid { get { return new Guid("8e2d966d-365f-45d8-a27b-109bf220cfc2"); } }

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
            pManager.AddLineParameter("Line", "L", "Line defining the element.", GH_ParamAccess.item);
            pManager.HideParameter(0);
            //pManager.AddIntegerParameter("Index of Optimization Group", "Grp", "All elements in a same group will have the same area after optimization.", GH_ParamAccess.item);
            pManager.AddGenericParameter("Cross section in Compression", "CS_Comp", "Cross section of the element when it is subjected to compression. This section is used to determine the volume of the element.", GH_ParamAccess.item);
            pManager[1].Optional = true;
            pManager.AddGenericParameter("Cross section in Tension", "CS_Tens", "Cross section of the element when it is subjected to tension", GH_ParamAccess.item);
            pManager[2].Optional = true;
            pManager.AddGenericParameter("Material in Compression", "M_Comp", "Material of the element when it is subjected to compression. This material is used to determine the mass of the element.", GH_ParamAccess.item);
            pManager[3].Optional = true;
            pManager.AddGenericParameter("Material in Tension", "M_Tens", "Material of the element when it is subjected to tension", GH_ParamAccess.item);
            pManager[4].Optional = true;
            pManager.AddTextParameter("Buckling Law", "Buckl law", "Choose a buckling law between \"Euler\", \"Rankine\", Eurocode (EN1993) curves \"a\",\"b\",\"c\",\"d\". \nNote that yielding law will apply if the inputted text does not exactly match any of the \"suggestions\".", GH_ParamAccess.item,"Not Applicable");
            pManager[5].Optional = true;
            pManager.AddNumberParameter("Buckling Factor", "k", "Buckling factor k defines the buckling length Lb such that Lb = k*L" , GH_ParamAccess.item, 1.0);
            pManager[6].Optional = true;
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Element - General", "E", "A general element", GH_ParamAccess.item);
        }



        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Line line = new Line();
            GH_CrossSection ghCS_Comp = new GH_CrossSection();
            GH_CrossSection ghCS_Tens = new GH_CrossSection();
            GH_Muscles_Material ghMat_Comp = new GH_Muscles_Material();
            GH_Muscles_Material ghMat_Tens = new GH_Muscles_Material();
            string law = " ";
            double k = 1.0;

            if (!DA.GetData(0, ref line)) { return; }
            if (!DA.GetData(1, ref ghCS_Comp)) {  }
            if (!DA.GetData(2, ref ghCS_Tens)) {  }
            if (!DA.GetData(3, ref ghMat_Comp)) {  }
            if (!DA.GetData(4, ref ghMat_Tens)) { }
            if (!DA.GetData(5, ref law)) { }
            if (!DA.GetData(6, ref k)) { }


            Element e = new Element(line, ghCS_Comp.Value, ghCS_Tens.Value,ghMat_Comp.Value,ghMat_Tens.Value,law,k);
            GH_Element gh_e = new GH_Element(e);
            DA.SetData(0, gh_e);
        }




        #endregion Methods
    }
}
