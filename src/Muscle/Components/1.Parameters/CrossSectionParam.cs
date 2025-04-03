// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

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
