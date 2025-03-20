using Grasshopper.Kernel;
using Muscle.View;
using System;
using System.Collections.Generic;
using System.Windows.Forms;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.Param
{
    public class CrossSectionParam : GH_PersistentParam<GH_CrossSection>
    {
        #region Properties


        #endregion Properties

        #region Constructors

        public CrossSectionParam() : base("Cross Section", "CS", "Contains a collection of cross sections", GHAssemblyName, Folder1_Param) { }
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
