using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles.Elements
{
    public class ElementResultsComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ElementResultsComponent()
          : base("Element's Results", "Elem Results",
              "Get the results of the elements after the structure has been solved.",
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
            pManager.AddLineParameter("Line", "L", "Line", GH_ParamAccess.item);
            pManager.AddBooleanParameter("Is Valid", "IsValid", "True if the total tension is in the interval of allowable tension.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Unity Check", "UC", "Tension Total/Tension Allowable or NAN if cables are compressed or struts are tensed", GH_ParamAccess.item);
            pManager.AddNumberParameter("Xsi", "Xsi", "Xsi = Reduction factor in compression = Buckling strength/Yielding strength", GH_ParamAccess.item); //2
            pManager.AddNumberParameter("Tension Additional", "t (kN)", "Additional Tension coming only from the last applied loads", GH_ParamAccess.item); //2
            pManager.AddNumberParameter("Tension Total", "t_tot (kN)", "Total Tension coming from all applied loads", GH_ParamAccess.item); //3
            pManager.AddIntervalParameter("Tension Allowable", "t allow (kN)", "Allowable Tension [-Buckling,Yielding]", GH_ParamAccess.item); //2
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();

            if (!DA.GetData(0, ref e)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetData(0, e.Line);
            DA.SetData(1, e.IsValid);
            DA.SetData(2, e.UC);
            DA.SetData(3, e.Xsi);
            int final = e.AxialForce_Results.Count - 1;
            if (final>=0)
            {
                DA.SetData(4, e.AxialForce_Results[final]/1e3);
                DA.SetData(5, e.AxialForce_Total[final]/1e3);
            }
            Interval kn = new Interval(e.AxialForce_Allowable.T0 / 1e3, e.AxialForce_Allowable.T1 / 1e3);
            DA.SetData(6, kn);

            //else
            //{
            //    DA.SetData(2,null);
            //    DA.SetData(3,null);
            //}

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
            get { return new Guid("a7c78f2a-bc16-4c84-93b2-2bb0c0ca009d"); }
        }
    }
}