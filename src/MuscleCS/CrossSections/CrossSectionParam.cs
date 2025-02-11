using Grasshopper.Kernel;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;


namespace Muscle.CrossSections
{
    public class ElementParam : GH_PersistentParam<GH_CrossSection>
    {
        #region Properties


        #endregion Properties

        #region Constructors

        public ElementParam() : base("Cross Section", "CS", "Contains a collection of cross sections", "Muscles", "Params") { }
        public override Guid ComponentGuid { get { return new Guid("96b876dc-49b2-43c4-97d8-f200720e57a2"); } }


        #endregion Constructors

        #region Methods

        protected override void Menu_AppendPromptMore(ToolStripDropDown menu) { }

        protected override void Menu_AppendPromptOne(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_CrossSection> values)
        {
            return GH_GetterResult.cancel; // to implement
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_CrossSection value)
        {
            return GH_GetterResult.cancel; // to implement
        }

        #endregion Methods
    }
}
