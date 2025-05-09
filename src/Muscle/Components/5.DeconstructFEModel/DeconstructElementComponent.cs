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

using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using MuscleApp.ViewModel;
using static Muscle.Components.GHComponentsFolders;
using Rhino.Geometry;

namespace Muscle.Components.DeconstructFEModel
{
    public class DeconstructElementComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DeconstructElementComponent()
          : base("Deconstruct Element", "DeElem",
              "Deconstruct an element to retrieve its properties.",
              GHAssemblyName, Folder5_DeconstructFEM)
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "Input finite element", GH_ParamAccess.item); //0
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Name", "name", "Element name", GH_ParamAccess.item); //0
            pManager.AddIntegerParameter("Element Index", "Idx", "Index of the element", GH_ParamAccess.item); //1
            pManager.AddIntegerParameter("End nodes indexes", "End nodes", "Indexes of the end nodes", GH_ParamAccess.list); //2
            pManager.AddLineParameter("Line", "L", "Current line and current length of the element", GH_ParamAccess.item); //3
            pManager.AddNumberParameter("Free length", "L0 (m)", "Free length of the element", GH_ParamAccess.item); //4
            pManager.AddGenericParameter("Cross Section", "CS", "Cross section of the element", GH_ParamAccess.item); //5
            pManager.AddGenericParameter("Material", "M", "Bilinear Material of the element", GH_ParamAccess.item); //6
            pManager.AddNumberParameter("Mass", "m (kg)", "Mass (kg) of the element", GH_ParamAccess.item); //7
            pManager.AddNumberParameter("Tension", "t (kN)", "Axial force (kN, tension positive, compression negative) in the element due to all applied loads and prestress", GH_ParamAccess.item); //8
            pManager.AddIntervalParameter("Resistances", "[tmin, tmax] (kN)", "Resistance interval [(-)Buckling resistance, (+)Yielding resistance] (kN)", GH_ParamAccess.item); //9
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();

            if (!DA.GetData(0, ref e)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetData(0, e.Name);
            DA.SetData(1, e.Idx);
            DA.SetDataList(2, e.EndNodes);
            DA.SetData(3, e.Line);
            DA.SetData(4, e.FreeLength);
            DA.SetData(5, e.CS);
            DA.SetData(6, e.Material);
            DA.SetData(7, e.Mass );
            DA.SetData(8, e.Tension / 1000);

            double Ryb = e.Resistance.T0 /1000; //kN
            double Ryt = e.Resistance.T1 /1000;
            DA.SetData(9, new Interval(Ryb, Ryt));
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("ac280579-ab96-4422-8c3c-00b88a4b6c2c"); }
        }
    }
}
