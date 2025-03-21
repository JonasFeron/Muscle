using Grasshopper.Kernel;
using Muscle.View;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Param
{
    public class PrestressParam : GH_PersistentParam<GH_Prestress>
    {
        #region Properties


        #endregion Properties

        #region Constructors

        public PrestressParam() : base("Prestress", "P", "Contains a collection of prestresses",  GHAssemblyName, Folder1_Param) { }
        public override Guid ComponentGuid { get { return new Guid("3fd9de05-73a4-4201-a3e5-a88cf934f119"); } }


        #endregion Constructors

        #region Methods

        protected override void Menu_AppendPromptMore(ToolStripDropDown menu) { }

        protected override void Menu_AppendPromptOne(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_Prestress> values)
        {
            return GH_GetterResult.cancel; // to implement
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_Prestress value)
        {
            return GH_GetterResult.cancel; // to implement
        }

        #endregion Methods
    }
}

