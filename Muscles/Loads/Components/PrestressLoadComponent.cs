using System;
using System.Collections.Generic;
using Muscles.Elements;

using Grasshopper.Kernel;
using Rhino.Geometry;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

namespace Muscles.Loads
{
    public class PrestressLoadComponent : GH_Component
    {

        public PrestressLoadComponent()
          : base("Create Prestress Loads", "P",
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
            get { return new Guid("ae51905c-0c73-48bd-b9d3-17c27c45c8de"); }
        }


        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "Element (General, Bar, Strut, or Cable) subjected to a prestress load.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Lengthening", "DL (m)", "Length variation in m (+ lengthening, - shortening) to apply on the element free length.",GH_ParamAccess.item);

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

            //2) Transform datas into InitialForce object
            PrestressLoad initialforce = new PrestressLoad(e, value);

            //3) output datas
            DA.SetData(0, new GH_PrestressLoad(initialforce));

        }
    }
}