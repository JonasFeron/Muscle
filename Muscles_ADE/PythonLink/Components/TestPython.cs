using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles_ADE.PythonLink.Component
{
    public class TestPython : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public TestPython()
          : base("TestPython", "test",
              "Test to see if python is well working.",
              "Muscles", "0. ToDoFirst")
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("TextToLower", "ToLower", "a test script", GH_ParamAccess.item);
            pManager.AddTextParameter("TextToUpper", "ToUpper", "a test script", GH_ParamAccess.item);

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Result text", "res", "string0.ToLower + string1.ToUpper", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            if (AccessToAll.pythonManager == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Please restart one \"Initialize Python\" Component.");
                return;
            }

            string str0 = "";
            string str1 = "";

            if (!DA.GetData(0, ref str0)) { return; }
            if (!DA.GetData(1, ref str1)) { return; }

            string result = null;
            if (AccessToAll.pythonManager != null)
            {
                result = AccessToAll.pythonManager.ExecuteCommand(AccessToAll.MainTest, str0, str1);
            }


            DA.SetData(0, result);
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
            get { return new Guid("cc03ae9a-4afa-4997-8afc-443b02bc5546"); }
        }
    }
}
