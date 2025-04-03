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
using Rhino.Geometry;
using System;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.ConstructFEModel
{
    /// <summary>
    /// Component that allows to create custom material.
    /// </summary>
    public class MaterialLinearComponent : GH_Component
    {


        #region Constructors

        /// <summary>
        /// This is the MaterialComponent Constructor. It uses base constructor to set name, nickname, description, category and subcategory of the component.
        /// </summary>
        public MaterialLinearComponent() : base("Construct Material - Linear", "M", "Define a material with linear properties", GHAssemblyName, Folder2_ConstructFEM) { }

        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("6af1c7f1-5c25-4581-bd22-2444d8327fc2"); } }

        /// <summary>
        /// Property to access component icon.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                // You can add image files to your project resources and access them like this:
                //return Resources.IconForThisComponent;
                return null;
            }
        }
        #endregion Constructors

        #region Methods


        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            // Registration of the material name input
            pManager.AddTextParameter("Name", "N", "Name of the material.", GH_ParamAccess.item, "Material");

            // Registration of the young modulus input
            pManager.AddNumberParameter("Young modulus", "E (MPa)", "Young modulus of the material in MPa. The same Young modulus is used in compression and in tension.", GH_ParamAccess.item, 0.0);

            // Registration of the yield strength input
            pManager.AddIntervalParameter("Yield strengths", "Fy (MPa)", "Linear elastic domain of the material [Compressive Yield Strength, Tensile Yield Strength] in MPa. Note: Compression is negative.", GH_ParamAccess.item, new Interval(double.NegativeInfinity, double.PositiveInfinity));

            // Registration of the density input
            pManager.AddNumberParameter("Specific mass", "\u03c1 (kg/m3)", "Density of the material in kg/m^3.", GH_ParamAccess.item, 0.0);
            pManager[0].Optional = true;
            pManager[1].Optional = true;
            pManager[2].Optional = true;
            pManager[3].Optional = true;
        }


        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            // Registration of the ouput
            pManager.AddGenericParameter("Material", "M", "Material containing physical properties.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // collect datas
            string name = "No Name";
            double young = 0.0; //value in MPa
            Interval fy = new Interval(double.NegativeInfinity, double.PositiveInfinity); //value in MPa
            double rho = 0.0; //value in kg/m3

            if (!DA.GetData(0, ref name)) { }
            if (!DA.GetData(1, ref young)) { }
            if (!DA.GetData(2, ref fy)) { }
            if (!DA.GetData(3, ref rho)) { }

            //process data

            var material = new BilinearMaterial(name, young * 1e6, young * 1e6, new Interval(fy.T0 *1e6, fy.T1 *1e6), rho); // E and fy are saved in Pa in the material object
            GH_BilinearMaterial gh_material = new GH_BilinearMaterial(material); // material is wrapped in a GH_material which can be interpreted by grasshopper

            // check data validity
            if (!gh_material.IsValid)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, gh_material.IsValidWhyNot);
                return;
            }

            // Set output value 
            DA.SetData(0, gh_material); //GH_material is sent to GH 
        }

        #endregion Methods

    }
}