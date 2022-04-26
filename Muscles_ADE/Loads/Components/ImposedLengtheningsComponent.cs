using System;
using System.Collections.Generic;
using Muscles_ADE.Elements;

using Grasshopper.Kernel;
using Rhino.Geometry;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

namespace Muscles_ADE.Loads 
{
    public class ImposedLenghteningsComponent : GH_Component
    {

        public ImposedLenghteningsComponent()
          : base("Create Imposed Lengthenings to prestress the structure", "DL",
              "Set the lengthenings to apply on the elements free lengths.",
              "Muscles", "Loads")
        {
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
            get { return new Guid("2a9d7252-bf3e-4284-89e7-c58ca290864f"); }
        }


        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "Element (General, Bar, Strut, or Cable) subjected to a prestress load.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Lengthening", "DL (m)", "Length variation in m (+ lengthening, - shortening) to apply on the element free length.", GH_ParamAccess.item);

        }


        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Lengthening", "DL (m)", "Length variation in m (+ lengthening, - shortening) to apply on the element free length.", GH_ParamAccess.item);
        }


        protected override void SolveInstance(IGH_DataAccess DA)
        {
            //1) Collect Data
            Element e = new Element();
            double value = 0.0;

            if (!DA.GetData(0, ref e)) { return; }
            if (!DA.GetData(1, ref value)) { return; }

            //2) Transform datas into ImposedLengthenings object
            ImposedLenghtenings DL = new ImposedLenghtenings(e, value);

            //3) output datas
            DA.SetData(0, new GH_ImposedLengthenings(DL));

        }
    }
}
