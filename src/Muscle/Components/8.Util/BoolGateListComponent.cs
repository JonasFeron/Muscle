using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Util
{
    public class BoolGateListComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public BoolGateListComponent()
          : base("Gate All/Any", "All/Any",
              "Perform operations \"AND\"/\"OR\" on a list of booleans",
              GHAssemblyName, Folder8_Util)
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddBooleanParameter("List", "list", "A list of boolean", GH_ParamAccess.list);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddBooleanParameter("All", "All", "return True if All items are True.", GH_ParamAccess.item);
            pManager.AddBooleanParameter("Any", "Any", "return True if Any item is True.", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            List<bool> list = new List<bool>();
            if (!DA.GetDataList(0, list)) { return; }
            if (list.Count == 0 || list == null) return;

            bool and = list[0];
            bool or = list[0];
            foreach (bool b in list)
            {
                and = b && and;
                or = b || or;
            }

            DA.SetData(0, and);
            DA.SetData(1, or);
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
            get { return new Guid("85b65471-313d-4209-a36f-2ad361c8be31"); }
        }
    }
}