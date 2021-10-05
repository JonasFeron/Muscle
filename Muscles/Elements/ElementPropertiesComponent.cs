using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles.Elements
{
    public class ElementPropertiesComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ElementPropertiesComponent()
          : base("Element Properties", "Elem prop",
              "Get the properties of elements.",
              "Muscles", "Elements")
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "The finite element(s).", GH_ParamAccess.item); //0
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Type", "type", "General, Bar, Strut or Cable.", GH_ParamAccess.item); //0
            pManager.AddIntegerParameter("Nodes Indexes", "ind", "The indexes of the extreme nodes.", GH_ParamAccess.list); //1
            pManager.AddLineParameter("Line", "L", "The line geometry of the finite element.", GH_ParamAccess.item); //2
            pManager.AddGenericParameter("Cross Section", "CS", "The cross section of the finite element.", GH_ParamAccess.item); //3
            pManager.AddGenericParameter("Material", "Mat", "The material of the finite element.", GH_ParamAccess.item); //4
            pManager.AddNumberParameter("Volume", "V (m³)", "Volume in m³.", GH_ParamAccess.item); //5
            pManager.AddNumberParameter("Mass", "m (kg)", "Mass in kg.", GH_ParamAccess.item); //6
            pManager.AddVectorParameter("Weight", "W (kN)", "Weight in kN", GH_ParamAccess.item); //7

        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();

            if (!DA.GetData(0, ref e)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetData(0, e.TypeName);
            DA.SetDataList(1, e.ExtremitiesIndex);
            DA.SetData(2, e.Line);
            DA.SetData(3, e.CS_Main);
            DA.SetData(4, e.Mat_Main);
            DA.SetData(5, e.V);
            DA.SetData(6, e.Mass);
            DA.SetData(7, e.Weight/1000);



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
            get { return new Guid("40100cb6-a980-4d65-b37e-7c169c32d1ce"); }
        }
    }
}