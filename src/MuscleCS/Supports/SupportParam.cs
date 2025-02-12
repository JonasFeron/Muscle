using System.Drawing;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Rhino.Geometry;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace Muscle.Supports
{
    public class SupportParam : GH_PersistentGeometryParam<GH_Support>, IGH_PreviewObject
    {

        #region Properties

        public BoundingBox ClippingBox
        {
            get
            {
                List<Point3d> points = new List<Point3d>();
                foreach (GH_Support ghSupport in VolatileData.AllData(true)) { points.Add(ghSupport.Value.Point); }
                foreach (GH_Support ghSupport in PersistentData.AllData(true)) { points.Add(ghSupport.Value.Point); }
                BoundingBox Bbox = new BoundingBox(points);
                Bbox.Inflate(3.0);

                return Bbox;
            }
        }
        public override Guid ComponentGuid { get { return new Guid("cafa0cb0-b40c-493d-87e3-cce41331ba71"); } }
        public bool Hidden { get; set; }
        public bool IsPreviewCapable { get { return true; } }
        protected override Bitmap Icon { get { return null; } }

        #endregion Properties

        #region Constructors

        public SupportParam() : base(new GH_InstanceDescription("Support", "Spt", "Contains a collection of supports", "Muscles", "Params"))
        {
        }

        #endregion Constructors
        #region Methods

        public void DrawViewportMeshes(IGH_PreviewArgs args)
        {
            Preview_DrawMeshes(args);
        }

        public void DrawViewportWires(IGH_PreviewArgs args)
        {
            Preview_DrawWires(args);
        }

        /// <summary>
        /// I don't know how to implement collection management so I'd rather remove it from the menu.
        /// </summary>
        /// <param name="menu"></param>
        protected override void Menu_AppendManageCollection(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_Support> gh_supports)
        {
            gh_supports = new List<GH_Support>();

            while (true)
            {
                GH_Support gh_support = null;
                switch (Prompt_Singular(ref gh_support))
                {
                    case GH_GetterResult.success:
                        gh_supports.Add(gh_support);
                        Rhino.RhinoApp.WriteLine("Set new support or press enter.");
                        break;

                    case GH_GetterResult.accept:
                        return GH_GetterResult.success;

                    case GH_GetterResult.cancel:
                        return GH_GetterResult.cancel;
                }
            }
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_Support gh_support)
        {
            GetPoint go = new GetPoint();
            go.AcceptNothing(true);
            go.AcceptPoint(true);

            OptionToggle toggleXfree = new OptionToggle(false, "Fixed", "Free");
            OptionToggle toggleYfree = new OptionToggle(false, "Fixed", "Free");
            OptionToggle toggleZfree = new OptionToggle(false, "Fixed", "Free");

            while (true)
            {
                go.ClearCommandOptions();
                go.SetCommandPrompt("Set support conditions by clicking on X Y Z then set a point");

                go.AddOptionToggle("X", ref toggleXfree);
                go.AddOptionToggle("Y", ref toggleYfree);
                go.AddOptionToggle("Z", ref toggleZfree);

                Rhino.Input.GetResult get = go.Get();
                if (get == Rhino.Input.GetResult.Nothing) { return GH_GetterResult.accept; }
                if (get == Rhino.Input.GetResult.Cancel) { return GH_GetterResult.cancel; }

                if (get == Rhino.Input.GetResult.Point)
                {
                    gh_support = new GH_Support(new Support(go.Point(), toggleXfree.CurrentValue, toggleYfree.CurrentValue, toggleZfree.CurrentValue));

                    return GH_GetterResult.success;
                }
            }
        }

        /// <summary>
        /// If different supports are defined on the same point, then only one support (merging the different support conditions) is kept per point. 
        /// </summary>
        protected override void CollectVolatileData_FromSources()
        {
            base.CollectVolatileData_FromSources();
            GH_Structure<GH_Support> merged_supports = new GH_Structure<GH_Support>();
            merged_supports.AppendRange(GH_Support.MergeConditionsOnSamePoint(m_data));
            m_data = merged_supports; // on change la référence vers la nouvelle liste avec les supports dont les conditions ont été rassemblées si plusieurs supports ont été définis sur un même noeud
        }


        #endregion Methods

    }
}