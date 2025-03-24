using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Util
{
    public class ToMatrixInput : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ToMatrixInput()
          : base("To Matrix Inputs", "Matrix Input",
              "Takes a tree as input and returns the 2D matrix inputs (rows, columns, values).",
            GHAssemblyName, Folder8_Util)

        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddNumberParameter("Tree", "T", "A tree that we want to convert into a 2D matrix", GH_ParamAccess.tree);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddIntegerParameter("Rows", "R", "Number of rows of the 2D matrix", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Columns", "C", "Number of columns of the 2D matrix", GH_ParamAccess.item);
            pManager.AddNumberParameter("Values", "V", "Matrix values", GH_ParamAccess.list);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            GH_Structure<GH_Number> tree = new GH_Structure<GH_Number>();
            if (!DA.GetDataTree(0, out tree)) { return; }

            int rows = tree.Branches.Count;
            int columns = tree.Branches[0].Count;
            var data = tree.FlattenData();
            if (data.Count != rows * columns)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "The inputted tree is not convertible to a 2D matrix");
            }
            DA.SetData(0, rows);
            DA.SetData(1, columns);
            DA.SetDataList(2, data);
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
            get { return new Guid("d256f4ed-b99e-46c1-8dd5-d3a80441b57c"); }
        }
    }
}