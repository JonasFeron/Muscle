using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles_ADE.Elements
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
            pManager.AddLineParameter("Line", "L", "Line", GH_ParamAccess.item); //0
            pManager.AddNumberParameter("Free length", "Free L (m)", "The length of the element free of any strain.", GH_ParamAccess.item); //1
            pManager.AddBooleanParameter("Is Valid", "IsValid", "True if the Tension is in the interval of allowable Tension.", GH_ParamAccess.item);//2
            pManager.AddNumberParameter("Unity Check", "UC", "Tension/Allowable Tension. The UC can be negative if the cables are compressed or struts are tensed", GH_ParamAccess.item);//3
            pManager.AddNumberParameter("Xsi", "Xsi", "Xsi = Reduction factor in compression = Buckling strength/Yielding strength", GH_ParamAccess.item); //4
            pManager.AddNumberParameter("Tension", "t (kN)", "Total Tension coming from all applied loads", GH_ParamAccess.item); //5
            pManager.AddIntervalParameter("Tension Allowable", "allow. t (kN)", "Allowable Tension [Buckling,Yielding]", GH_ParamAccess.item); //6
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();

            if (!DA.GetData(0, ref e)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetData(0, e.Line);
            DA.SetData(1, e.LFree);
            DA.SetData(2, e.IsValid);
            DA.SetData(3, e.UC);
            DA.SetData(4, e.Xsi);
            DA.SetData(5, e.Tension / 1000);
            Interval allow = new Interval(e.AllowableTension.T0 / 1e3, e.AllowableTension.T1 / 1e3);
            DA.SetData(6, allow);

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
            get { return new Guid("140b4830-2b26-4971-9670-2ef9995c8d24"); }
        }
    }
}