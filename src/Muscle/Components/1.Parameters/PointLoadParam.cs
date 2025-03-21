using Grasshopper.Kernel;
using Muscle.View;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Param
{
    public class PointLoadParam : GH_PersistentParam<GH_PointLoad>
    {
        #region Properties


        #endregion Properties

        #region Constructors

        public PointLoadParam() : base("Point Load", "Load", "Contains a collection of point loads",  GHAssemblyName, Folder1_Param) { }
        public override Guid ComponentGuid { get { return new Guid("e214aac1-ec39-4c8b-800e-d38193bdc5e6"); } }


        #endregion Constructors

        #region Methods

        protected override void Menu_AppendPromptMore(ToolStripDropDown menu) { }

        protected override void Menu_AppendPromptOne(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_PointLoad> values)
        {
            return GH_GetterResult.cancel; // to implement
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_PointLoad value)
        {
            return GH_GetterResult.cancel; // to implement
        }

        #endregion Methods
    }
}

