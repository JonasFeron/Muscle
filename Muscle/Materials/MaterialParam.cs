using Grasshopper.Kernel;
using Rhino.Input.Custom;
using System;
using System.Collections.Generic;
using System.Windows.Forms;

namespace Muscle.Materials
{
    public class MaterialParam : GH_PersistentParam<GH_Muscles_Material>
    {


        #region Constructors

        /// <summary>
        /// This is the parameter constructor. It uses base constructor to set name, nickname, description, category and subcategory of the parameter.
        /// </summary>
        public MaterialParam() : base("Material", "M", "Contains a collection of materials.", "Muscles", "Params") { }


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

        protected override GH_GetterResult Prompt_Plural(ref List<GH_Muscles_Material> values)
        {
            values = new List<GH_Muscles_Material>();

            while (true)
            {
                GH_Muscles_Material value = null;
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

        protected override GH_GetterResult Prompt_Singular(ref GH_Muscles_Material value)
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
                    value = new GH_Muscles_Material(new Muscles_Material(go.StringResult(), toggleYoung.CurrentValue * 1e6, toggleFy.CurrentValue * 1e6, toggleRho.CurrentValue));
                    return GH_GetterResult.success;
                }
            }
        }

        #endregion Methods

    }
}
