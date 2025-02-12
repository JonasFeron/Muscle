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
using Muscle.PythonConnectedComponents.TwinObjects;
using Newtonsoft.Json;
using PythonConnect;


namespace Muscle.PythonConnectedComponents
{
    public class aPythonConnectedGHComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        public aPythonConnectedGHComponent()
          : base("aPythonConnectedComponent", "ExecutePython",
                "This is a component that shows how to transfer complex data between the main Grasshopper/C# thread and the (parallel) python thread.\n" +
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
            string dataPath = Path.Combine(AccessToAll.tempDirectory, "complex_script_TwinData.txt"); // The main C# thread will write the data to the file, and the python thread will read it.
            string resultPath = Path.Combine(AccessToAll.tempDirectory, "complex_script_TwinResult.txt"); // The python thread will write the results to the file, and the main C# thread will read it.
            string pythonScript = "complex_script.py"; // ensure that the python script is located in AccessToAll.pythonProjectDirectory, or provide the relative path to the script.

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

            //1) Collect Data

            var list = new List<GH_Number>();
            int row = 0;
            int col = 0;

            if (!DA.GetDataList(0, list)) { return; }
            if (!DA.GetData(1, ref row)) { return; }
            if (!DA.GetData(2, ref col)) { return; }


            //2) Solve in python


            var twinData = new TwinData(list, row, col); 
            var twinResult = new TwinResult();


            //convert the TwinData object into a string (with JSON format)
            string dataString = JsonConvert.SerializeObject(twinData, Formatting.None);

            string resultString = AccessToAll.pythonManager.ExecuteCommand(pythonScript, dataPath, resultPath, dataString);
            foreach (string errorMessage in PythonManager.GetErrorMessages())
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, errorMessage);
            }

            //convert the result (contained in a string) into a TwinResult object
            try
            {
                JsonConvert.PopulateObject(resultString, twinResult);
            }
            catch (Exception e)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"python result= {resultString}");
                return;
            }

            //3) return the result
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
            get { return new Guid("7e35c61f-3bd0-4e8d-8e37-de5f7e7d363b"); }
        }

    }
}