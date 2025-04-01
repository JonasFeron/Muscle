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
using MuscleApp.ViewModel;
using System;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.DeconstructFEModel
{

    public class DeconstructMaterialComponent : GH_Component
    {

        #region Properties



        #endregion Properties

        #region Constructors

        /// <summary>
        /// Get the mechanical properties of a material.
        /// </summary>
        public DeconstructMaterialComponent() : base("Deconstruct Material", "DeMat", "Deconstruct a bilinear material to retrieve its properties.", GHAssemblyName, Folder5_DeconstructFEM) { }


        /// <summary>
        /// This is the Global Unique IDentifier (GUID) of the component. It's a unique value that allow to identify the component as itself. DO NOT change it.
        /// </summary>
        public override Guid ComponentGuid { get { return new Guid("fdfb5faf-64ac-436b-ab95-f437685aadc1"); } }
        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            // Registration of the material input
            pManager.AddGenericParameter("Material", "M", "Material", GH_ParamAccess.item);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            // Registration of the material name input
            pManager.AddTextParameter("Name", "N", "Name of the material.", GH_ParamAccess.item);

            // Registration of the yield strength input
            pManager.AddIntervalParameter("Yield strengths", "Fy (MPa)", "Linear elastic domain of the material [Compressive Yield Strength, Tensile Yield Strength] in MPa.", GH_ParamAccess.item);

            // Registration of the young modulus input
            pManager.AddNumberParameter("Compressive Young modulus", "Ec (MPa)", "Compressive Young modulus of the material in MPa.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Tensile Young modulus", "Et (MPa)", "Tensile Young modulus of the material in MPa.", GH_ParamAccess.item);

            // Registration of the density input
            pManager.AddNumberParameter("Specific Mass", "\u03c1 (kg/m3)", "Density of the material in kg/m^3.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            BilinearMaterial material = null;

            if (!DA.GetData(0, ref material)) { return; }

            var LinearElasticDomain = new Interval(material.Fyc * 1e-6, material.Fyt * 1e-6);

            DA.SetData(0, material.Name);
            DA.SetData(1, LinearElasticDomain);
            DA.SetData(2, material.Ec * 1e-6);
            DA.SetData(3, material.Et * 1e-6);
            DA.SetData(4, material.Rho);
        }

        #endregion Methods

    }
}