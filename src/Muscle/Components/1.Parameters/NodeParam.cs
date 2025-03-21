using Grasshopper.Kernel;
using Muscle.View;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Param
{
    public class NodeParam : GH_PersistentParam<GH_Node>
    {
        #region Properties


        #endregion Properties

        #region Constructors

        public NodeParam() : base("Node", "N", "Contains a collection of nodes",  GHAssemblyName, Folder1_Param) { }
        public override Guid ComponentGuid { get { return new Guid("9568793f-1347-46d6-a3c7-10c4530906a9"); } }


        #endregion Constructors

        #region Methods

        protected override void Menu_AppendPromptMore(ToolStripDropDown menu) { }

        protected override void Menu_AppendPromptOne(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_Node> values)
        {
            return GH_GetterResult.cancel; // to implement
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_Node value)
        {
            return GH_GetterResult.cancel; // to implement
        }

        #endregion Methods
    }
}

