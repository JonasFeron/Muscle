// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

// PythonNETGrasshopperTemplate

// Copyright <2025> <Jonas Feron>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

// PythonConnectedGrasshopperTemplate

// Copyright < 2021 - 2025 > < Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of PythonConnectedGrasshopperTemplate: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

using System;
using Grasshopper.Kernel;
using System.IO;
// using MuscleCore.PythonNETInit;
using MuscleApp.PythonNETInit;

using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.PythonNETInit
{
    public class StartPythonNETComponent : GH_Component
    {
        private string _defaultAnacondaPath = PythonNET.DefaultAnacondaPath;
        private string _defaultCondaEnvName = PythonNET.DefaultCondaEnvName;
        private string _defaultPythonDllName = PythonNET.DefaultPythonDllName;
        public StartPythonNETComponent()
          : base("StartPython.NET", "StartPy",
              "Initialize Python.NET before running any calculation", GHAssemblyName, Folder0_PythonInit)
        {
            Grasshopper.Instances.DocumentServer.DocumentRemoved += DocumentClose;
        }


        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddBooleanParameter("Start Python", "Start", "Connect here a toggle. If true, Python/Anaconda starts and can calculate.", GH_ParamAccess.item);

            pManager.AddTextParameter("Anaconda Path", "conda", "Path to the directory where Anaconda3 is installed.", GH_ParamAccess.item, _defaultAnacondaPath);
            pManager[1].Optional = true;
            pManager.AddTextParameter("conda Environment Name", "condaEnv", "Name of the conda environment to activate, where musclepy is installed.", GH_ParamAccess.item, _defaultCondaEnvName);
            pManager[2].Optional = true;
            pManager.AddTextParameter("python3xx.dll", ".dll", "Name of the \"python3xx.dll\" file contained in the specified conda environment", GH_ParamAccess.item, _defaultPythonDllName);
            pManager[3].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            //1) Initialize and Collect Data
            bool start = false;
            string anacondaPath = _defaultAnacondaPath;
            string condaEnvName = _defaultCondaEnvName;
            string pythonDllName = _defaultPythonDllName;

            if (!DA.GetData(0, ref start)) return;
            if (!DA.GetData(1, ref anacondaPath)) return;
            if (!DA.GetData(2, ref condaEnvName)) return;
            if (!DA.GetData(3, ref pythonDllName)) return;

            //2) Check validity of user input and configure Python.NET
            bool success = false;
            try
            {
                success = PythonNET.TryConfiguring(anacondaPath, condaEnvName, pythonDllName);
            }
            catch (Exception ex)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, ex.Message);
                return;
            }
            
            var userConfig = PythonNET.UserConfig;
            if (!success || userConfig == null || !userConfig.IsValid)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python.NET configuration failed.");
                return;
            }

            AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, $"A valid Anaconda3 installation was found: {userConfig.AnacondaPath}");
            AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, $"\"{userConfig.CondaEnvName}\" environment has a valid python.exe");
            AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, $"{userConfig.PythonDllName} is a valid .dll file");

            // finally
            // {

            //     if (!userConfig.HasValidAnacondaPath)
            //     {
            //         AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Invalid Anaconda path.");
            //     }
            //     if (!userConfig.HasValidCondaEnvPath)
            //     {
            //         AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Invalid conda environment name.");
            //     }
            //     if (!userConfig.HasValidPythonDllName)
            //     {
            //         AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Invalid python3xx.dll name.");
            //     }
            // }



            //3) Initialize Python.NET, following https://github.com/pythonnet/pythonnet/wiki/Using-Python.NET-with-Virtual-Environments

            if (start && PythonNET.IsInitialized)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python.NET is already started.");
                return;
            }
            if (start && !PythonNET.IsInitialized) 
            {
                try
                {
                    PythonNET.Launch(userConfig);
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "Python.NET setup completed successfully.");
                    // AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "NumPy test passed: cos(2*pi) = 1");
                    // AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "MusclePy package found and validated.");
                    // AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "MusclePy test_script.py successfull.");
                }
                catch (Exception ex)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, ex.Message);
                }
            }

            if (!start)
            {
                try
                {
                    PythonNET.ShutDown();
                }
                catch (Exception ex)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, ex.Message);
                }
            }
            if (!PythonNET.IsInitialized)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, $"Python.NET is closed. Please restart Python.NET.");
            }

        }

        /// <summary>
        /// When Grasshopper is closed, stop the PythonNETInit engine.
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="doc"></param>
        private void DocumentClose(GH_DocumentServer sender, GH_Document doc)
        {
            PythonNET.ShutDown();
        }


        // /// <summary>
        // /// Checks the user input for validity and sets the configuration accordingly.
        // /// </summary>
        // /// <param name="anacondaPath">The path to the Anaconda installation directory.</param>
        // /// <param name="condaEnvName">The name of the conda environment to activate.</param>
        // /// <param name="pythonDllName">The name of the python DLL file.</param>
        // private void ConfigurePythonNET(string anacondaPath, string condaEnvName, string pythonDllName)
        // {
        //     //anacondaPath
        //     try
        //     {
        //         PythonNETConfig.anacondaPath = anacondaPath;
        //     }
        //     catch (ArgumentException e)
        //     {
        //         string default_msg = $"Please provide a valid path, similar to: {default_anacondaPath}";
        //         if (anacondaPath == default_anacondaPath)
        //         {
        //             AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Impossible to find a valid Anaconda3 Installation. " + default_msg);
        //             return;
        //         }
        //         else
        //         {
        //             AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message + default_msg);
        //             return;
        //         }
        //     }

        //     //condaEnvName
        //     try
        //     {
        //         PythonNETConfig.condaEnvName = condaEnvName;
        //     }
        //     catch (ArgumentException e)
        //     {
        //         AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
        //         return;
        //     }

        //     //pythonDllName
        //     try
        //     {
        //         PythonNETConfig.pythonDllName = pythonDllName;
        //     }
        //     catch (ArgumentException e)
        //     {
        //         AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
        //         return;
        //     }
        // }


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
            get { return new Guid("c3825588-91bb-4834-a65b-a497f5cf9a3b"); }
        }









    }

}
