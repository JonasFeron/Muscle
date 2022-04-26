using Grasshopper.Kernel;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace Muscles_ADE.Elements
{
    public class ElementParam : GH_PersistentParam<GH_Element>
    {
        #region Properties


        #endregion Properties

        #region Constructors

        public ElementParam() : base("Element", "E", "Contains a collection of finite elements", "Muscles", "Params") { }
        public override Guid ComponentGuid { get { return new Guid("176cdec4-1b1e-4426-87dc-260aed5b56b2"); } }


        #endregion Constructors

        #region Methods

        protected override void Menu_AppendPromptMore(ToolStripDropDown menu) { }

        protected override void Menu_AppendPromptOne(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_Element> values)
        {
            return GH_GetterResult.cancel; // to implement
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_Element value)
        {
            return GH_GetterResult.cancel; // to implement
        }

        #endregion Methods
    }
}

