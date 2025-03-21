using Grasshopper.Kernel;
using Muscle.View;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Param
{
    public class TrussParam : GH_PersistentParam<GH_Truss>
    {
        #region Properties


        #endregion Properties

        #region Constructors

        public TrussParam() : base("Structure", "struct", "Contains a collection of structures",  GHAssemblyName, Folder1_Param) { }
        public override Guid ComponentGuid { get { return new Guid("b067bf72-c0f6-41e8-bb20-a3f4836f2e5a"); } }


        #endregion Constructors

        #region Methods

        protected override void Menu_AppendPromptMore(ToolStripDropDown menu) { }

        protected override void Menu_AppendPromptOne(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_Truss> values)
        {
            return GH_GetterResult.cancel; // to implement
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_Truss value)
        {
            return GH_GetterResult.cancel; // to implement
        }

        #endregion Methods
    }
}

