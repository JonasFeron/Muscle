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
using MuscleApp.ViewModel;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Param
{
    public class BilinearMaterialParam : GH_PersistentParam<GH_BilinearMaterial>
    {


        #region Constructors

        /// <summary>
        /// This is the parameter constructor. It uses base constructor to set name, nickname, description, category and subcategory of the parameter.
        /// </summary>
        public BilinearMaterialParam() : base("Material", "M", "Contains a collection of bilinear materials.",  GHAssemblyName, Folder1_Param) { }


        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the parameter. It's a unique value that allow to identify the parameter as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("b3b4aef8-a88d-4f0d-ba64-84bf72bed615"); } }

        #endregion Constructors

        #region Methods

        /// <summary>
        /// The method override the initial one with an empty method to remove unwanted "Manage data" button.
        /// </summary>
        /// <param name="menu"></param>
        protected override void Menu_AppendManageCollection(ToolStripDropDown menu) { }

        protected override GH_GetterResult Prompt_Plural(ref List<GH_BilinearMaterial> values)
        {
            values = new List<GH_BilinearMaterial>();

            while (true)
            {
                GH_BilinearMaterial value = null;
                switch (Prompt_Singular(ref value))
                {
                    case GH_GetterResult.success:
                        values.Add(value);
                        Rhino.RhinoApp.WriteLine("Set new material or press enter.");
                        break;

                    case GH_GetterResult.accept:
                        return GH_GetterResult.success;

                    case GH_GetterResult.cancel:
                        return GH_GetterResult.cancel;
                }
            }
        }

        protected override GH_GetterResult Prompt_Singular(ref GH_BilinearMaterial value)
        {
            GetString go = new GetString();

            go.SetCommandPrompt("Enter the name of the material after having configured it:");
            go.AcceptNothing(true);

            OptionDouble toggleFy = new OptionDouble(235.0, true, 1e-3);
            OptionDouble toggleYoung = new OptionDouble(210000.0, true, 1e-3);
            OptionDouble toggleRho = new OptionDouble(7850, true, 0.0);

            while (true)
            {
                go.ClearCommandOptions();

                int optFy = go.AddOptionDouble("YieldStrength", ref toggleFy, "Enter the yield strength of the material in MPa");
                int optYoung = go.AddOptionDouble("YoungModulus", ref toggleYoung, "Enter the young modulus of the material in MPa");
                int optRho = go.AddOptionDouble("Density", ref toggleRho, "Enter the density of the material in kg/m^3");

                Rhino.Input.GetResult get = go.Get();
                if (get == Rhino.Input.GetResult.Cancel) { return GH_GetterResult.cancel; }
                if (get == Rhino.Input.GetResult.Nothing) { return GH_GetterResult.accept; }
                if (get == Rhino.Input.GetResult.String)
                {
                    // Use the 6-parameter constructor: name, Ec, Et, Fyc, Fyt, rho
                    double E = toggleYoung.CurrentValue * 1e6;  // Convert from MPa to N/m²
                    double Fy = toggleFy.CurrentValue * 1e6;    // Convert from MPa to N/m²
                    value = new GH_BilinearMaterial(new BilinearMaterial(go.StringResult(), E, E, -Fy, Fy, toggleRho.CurrentValue));
                    return GH_GetterResult.success;
                }
            }
        }

        #endregion Methods

    }
}
