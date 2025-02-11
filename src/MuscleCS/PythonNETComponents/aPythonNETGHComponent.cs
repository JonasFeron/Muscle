//PythonNETGrasshopperTemplate

//Copyright <2025> <Jonas Feron>

//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.

//List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
//Description and complete License: see NOTICE file.

//this file was imported from https://github.com/JonasFeron/PythonConnectedGrasshopperTemplate and is used WITH modifications.
//------------------------------------------------------------------------------------------------------------

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
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.PythonNETComponents.TwinObjects;
using Newtonsoft.Json;
using Python.Runtime;


namespace Muscle.PythonNETComponents
{
    public class aPythonNETGHComponent : GH_Component
    {

        public aPythonNETGHComponent()
          : base("aPythonNETComponent", "ExecutePython.NET",
                "This is a component that shows how to transfer complex data between the main Grasshopper/C# component and the python script.\n" +
                "For instance:\n" +
                "this script takes as input in Grasshopper/C#: a list, a number of columns and a number of rows \n" +
                "These input are sent to python\n" +
                "Python turns the list into a Numpy array of shape (rowNumber,colNumber)\n" +
                "then the Numpy array is returned in C#/Grasshopper as a Tree",
              AccessToAll.GHAssemblyName, AccessToAll.GHComponentsFolder1)
        {
        }

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddNumberParameter("A List of Numbers", "list", "A list of numbers to be converted in python into a Numpy array with rowNumber rows and colNumber columns", GH_ParamAccess.list);
            pManager.AddIntegerParameter("Row Number", "rowNumber", "The Number of Rows of the returned Numpy array", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Column Number", "colNumber", "The Number of Columns of the returned Numpy array", GH_ParamAccess.item);
        }

        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddNumberParameter("Grasshopper tree", "tree", "A python numpy array converted back into a Grasshopper tree", GH_ParamAccess.tree);
        }


        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string pythonScript = "complex_script"; // ensure that the python script is located in AccessToAll.pythonProjectDirectory, or provide the relative path to the script.

            if (!AccessToAll.hasPythonStarted)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }
            if (!File.Exists(Path.Combine(AccessToAll.pythonProjectDirectory, pythonScript+".py")))
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Please ensure that \"{pythonScript}\" is located in: {AccessToAll.pythonProjectDirectory}");
                return;
            }

            //1) Collect Data

            var list = new List<GH_Number>();
            int row = 0;
            int col = 0;

            if (!DA.GetDataList(0, list)) { return; }
            if (!DA.GetData(1, ref row)) { return; }
            if (!DA.GetData(2, ref col)) { return; }

            var twinData = new TwinData(list, row, col);
            string jsonData = JsonConvert.SerializeObject(twinData, Formatting.None);
            // Another way to convert the data from C# to Python (and back) exists if required: https://pythonnet.github.io/pythonnet/codecs.html

            var twinResult = new TwinResult();
            dynamic jsonResult = null;

            //2) Solve in python
            var m_threadState = PythonEngine.BeginAllowThreads();

            // following code is inspired by https://github.com/pythonnet/pythonnet/wiki/Threading
            // Don't access Python up here.
            using (Py.GIL())
            {
                // Safe to access Python here.
                try
                {
                    dynamic script = PyModule.Import(pythonScript);
                    dynamic mainFunction = script.main_json_example;
                    jsonResult = mainFunction(jsonData);
                    JsonConvert.PopulateObject((string)jsonResult, twinResult);
                }
                catch (PythonException ex)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, ex.Message);
                }
                catch (Exception e)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"python result= {jsonResult}");
                    return;
                }
            }
            // The following is unsafe: it is accessing a Python attribute without holding the GIL.
            //DA.SetData(0, jsonResult);

            PythonEngine.EndAllowThreads(m_threadState);


            //3) postprocess and return the result to Grasshopper
            List<List<double>> matrix = twinResult.Matrix;
            GH_Structure<GH_Number> gh_structure = TwinResult.ListListToGH_Struct(matrix); //convert the result into a Grasshopper tree

            DA.SetDataTree(0, gh_structure);
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
            get { return new Guid("9ade90e6-5914-412c-83c1-1fd9af567802"); }
        }

    }
}