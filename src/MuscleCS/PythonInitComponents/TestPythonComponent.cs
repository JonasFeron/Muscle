//Copyright < 2021 - 2025 > < Université catholique de Louvain (UCLouvain)>

//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.

//List of the contributors to the development of PythonConnectedGrasshopperTemplate: see NOTICE file.
//Description and complete License: see NOTICE file.
//------------------------------------------------------------------------------------------------------------

using System;
using System.Collections.Generic;
using System.IO;
using Grasshopper.Kernel;
using PythonConnect;
using Rhino.Geometry;

namespace Muscle.PythonInitComponents
{
    public class TestPythonComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        public TestPythonComponent()
          : base("TestPython", "test",
              "Test to check if python works well.",
              AccessToAll.GHAssemblyName, AccessToAll.GHComponentsFolder0)
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        /// <param name="pManager">The input parameter manager.</param>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("TextToLower", "ToLower", "a string argument to be lowercase", GH_ParamAccess.item);
            pManager.AddTextParameter("TextToUpper", "ToUpper", "a string argument to be uppercase", GH_ParamAccess.item);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        /// <param name="pManager">The output parameter manager.</param>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Result text", "result", "string0.ToLower + string1.ToUpper", GH_ParamAccess.item);
        }

        /// <summary>
        /// This Grasshopper component executes the Python script "test_script.py" with the arguments "str0" and "str1".
        /// </summary>
        /// <param name="DA">The data access object for retrieving input and setting output.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string dataPath = Path.Combine(AccessToAll.tempDirectory, "test_script_data.txt"); // The main C# thread will write the data to the file, and the python thread will read it.
            string resultPath = Path.Combine(AccessToAll.tempDirectory, "test_script_result.txt"); // The python thread will write the results to the file, and the main C# thread will read it.
            string pythonScript = "test_script.py"; // ensure that the python script is located in AccessToAll.pythonProjectDirectory, or provide the relative path to the script.

            if (AccessToAll.pythonManager == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Restart the \"StartPythonComponent\".");
                DA.SetData(0, null);
                return;
            }
            if (!File.Exists(Path.Combine(AccessToAll.pythonProjectDirectory, pythonScript)))
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Please ensure that \"{pythonScript}\" is located in: {AccessToAll.pythonProjectDirectory}");
                DA.SetData(0, null);
                return;
            }


            string str0 = "";
            string str1 = "";

            if (!DA.GetData(0, ref str0)) { return; }
            if (!DA.GetData(1, ref str1)) { return; }

            string result = AccessToAll.pythonManager.ExecuteCommand(pythonScript, dataPath, resultPath, str0, str1);

            foreach (string errorMessage in PythonManager.GetErrorMessages())
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, errorMessage);
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
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("a1bbd7fc-6605-4f5c-b3f7-889d696395bf"); }
        }
    }
}
