﻿// Muscle

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
using Rhino.Geometry;
using System;
using System.Windows.Forms;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.ConstructFEModel
{
    public class ElementComponent : GH_Component
    {
        public bool displayIn3d { get; set; }

        public static readonly string[] _bucklingLaws= {"Yielding", "Euler", "Rankine", "a", "b", "c", "d", "Slack"};
        public static readonly int[] _bucklingLawsIdx = { 0, -1, -2, 1, 2, 3, 4, 10};


        public ElementComponent() : base("Construct Element", "E", "A finite element is constructed from a line, a cross-section and a material.", GHAssemblyName, Folder2_ConstructFEM) 
        {
            displayIn3d = true; 
        }
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("6ed9ee2a-591e-42bb-973a-d239316c60fa"); } }

        public override void AppendAdditionalMenuItems(ToolStripDropDown menu)
        {
            base.AppendAdditionalMenuItems(menu);
        }

        public override bool AppendMenuItems(ToolStripDropDown menu)
        {
            //Menu_AppendItem(menu, "Display in 3D", displayClick, true, displayIn3d);
            //Menu_AppendItem(menu, "Display as line", displayClick, true, !displayIn3d);
            //Menu_AppendSeparator(menu);
            return base.AppendMenuItems(menu);
        }

        public void displayClick(object sender, EventArgs e)
        {
            displayIn3d = !displayIn3d;
        }

        protected override void AppendAdditionalComponentMenuItems(ToolStripDropDown menu)
        {
            base.AppendAdditionalComponentMenuItems(menu);
        }

        #endregion Properties

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddLineParameter("Line", "L", "Line defining the element.", GH_ParamAccess.item);
            pManager.HideParameter(0);
            pManager.AddGenericParameter("Cross section", "CS", "Cross section of the element.", GH_ParamAccess.item);
            pManager[1].Optional = true;
            pManager.AddGenericParameter("Material", "M", "Material of the element.", GH_ParamAccess.item);
            pManager[2].Optional = true;
            pManager.AddTextParameter("Element Name", "Name", "Name of the element", GH_ParamAccess.item, "Element");
            pManager[3].Optional = true;
            pManager.AddIntegerParameter("Buckling Law", "B. law", "Choose a buckling law between \"Euler\", \"Rankine\", Eurocode (EN1993) curves \"a\",\"b\",\"c\",\"d\".\n \"Yielding\" law corresponds to buckling strength = yielding strength.\n \"Slack\" law cancels the strength in compression (but not the young modulus! -> for non-linear analysis of slack cables with 0 stiffness in compression, use tension only material).", GH_ParamAccess.item, 0);
            pManager[4].Optional = true;
            pManager.AddNumberParameter("Buckling Factor", "k", "Buckling factor k defines the buckling length Lb such that Lb = k*Lfree", GH_ParamAccess.item, 1.0);
            pManager[5].Optional = true;

            // create a dropdown list for the user to select a supported buckling law
            var laws = pManager[4] as Grasshopper.Kernel.Parameters.Param_Integer;
            for (int i = 0; i < _bucklingLaws.Length; i++)
            {
                string law = _bucklingLaws[i];
                int idx = _bucklingLawsIdx[i];
                laws.AddNamedValue(law, idx);
            }
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "Element", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Line line = new Line();
            GH_CrossSection ghCS = new GH_CrossSection();
            GH_BilinearMaterial ghMat = new GH_BilinearMaterial();
            string name = " ";
            int lawIdx = 0; // index of the selected buckling law
            double k = 1.0; // buckling factor


            if (!DA.GetData(0, ref line)) { return; }
            if (!DA.GetData(1, ref ghCS)) { }
            if (!DA.GetData(2, ref ghMat)) { }
            if (!DA.GetData(3, ref name)) { }
            if (!DA.GetData(4, ref lawIdx)) { }
            if (!DA.GetData(5, ref k)) { }

            int index = Array.IndexOf(_bucklingLawsIdx, lawIdx);
            if (index == -1)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, $"Please choose a valid Buckling Law from the provided input list");
                lawIdx = 0;
                index = Array.IndexOf(_bucklingLawsIdx, lawIdx);
            }
            string law = _bucklingLaws[index];


            Element e = new Element(line, ghCS.Value, ghMat.Value, name, law, k);
            GH_Element gh_e = new GH_Element(e);

            DA.SetData(0, gh_e);
        }

        #endregion Methods
    }
}

