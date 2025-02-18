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
using Grasshopper.Kernel;
using System.IO;
using Python.Runtime;

namespace Muscle.PythonInitComponents
{
    public class StartPythonNETComponent : GH_Component
    {
        #region Properties
        private static string default_anacondaPath
        {
            get
            {
                if (AccessToAll.anacondaPath != null)
                {
                    return AccessToAll.anacondaPath;
                }
                else
                {
                    return @"C:\Users\Me\Anaconda3";
                }
            }
        }
        private static readonly string default_condaEnvName = "base";
        private static string default_pythonDllName
        {
            get
            {
                if (AccessToAll.pythonDllName != null)
                {
                    return AccessToAll.pythonDllName;
                }
                else
                {
                    return @"python3xx.dll";
                }
            }
        }

        #endregion Properties

        public StartPythonNETComponent()
          : base("StartPython.NET", "StartPy",
              "Initialize Python.NET before running any calculation", AccessToAll.GHAssemblyName, AccessToAll.GHComponentsFolder0)
        {
            Grasshopper.Instances.DocumentServer.DocumentRemoved += DocumentClose;
        }


        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddBooleanParameter("Start Python", "Start", "Connect here a toggle. If true, Python/Anaconda starts and can calculate.", GH_ParamAccess.item);

            pManager.AddBooleanParameter("User mode", "user", "true for user mode, false for developer mode.", GH_ParamAccess.item, true);
            pManager[1].Optional = true;
            pManager.AddTextParameter("Anaconda Directory", "condaPath", "Path to the directory where Anaconda3 is installed.", GH_ParamAccess.item, default_anacondaPath);
            pManager[2].Optional = true;
            pManager.AddTextParameter("conda Environment Name", "condaEnv", "Name of the conda environment to activate.", GH_ParamAccess.item, default_condaEnvName);
            pManager[3].Optional = true;
            pManager.AddTextParameter("python3xx.dll file", ".dll", "Name of the \"python3xx.dll\" file contained in the specified conda environment", GH_ParamAccess.item, default_pythonDllName);
            pManager[4].Optional = true;

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
            bool _user_mode = true;
            string _anacondaPath = default_anacondaPath;
            string _condaEnvName = default_condaEnvName;
            string _pythonDllName = default_pythonDllName;

            if (!DA.GetData(0, ref start)) return;
            if (!DA.GetData(1, ref _user_mode)) return;
            if (!DA.GetData(2, ref _anacondaPath)) return;
            if (!DA.GetData(3, ref _condaEnvName)) return;
            if (!DA.GetData(4, ref _pythonDllName)) return;



            //2) Check validity of Data ?
            #region Check Data
            AccessToAll.user_mode = _user_mode;

            if (AccessToAll.user_mode && !Directory.Exists(AccessToAll.rootDirectory))
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Check that {AccessToAll.GHAssemblyName} has been correctly installed in: {AccessToAll.specialFolder}");
                return;
            }
            if (!AccessToAll.user_mode && !Directory.Exists(AccessToAll.rootDirectory)) //Developer mode
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Check the path to {AccessToAll.rootDirectory}");
                return;
            }


            try
            {
                AccessToAll.anacondaPath = _anacondaPath;
            }
            catch (ArgumentException e)
            {
                string default_msg = $"Please provide a valid path, similar to: {default_anacondaPath}";
                if (_anacondaPath == default_anacondaPath)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Impossible to find a valid Anaconda3 Installation. " + default_msg);
                    return;
                }
                else
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message + default_msg);
                    return;
                }
            }
            AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, $"A valid Anaconda3 installation was found here: {AccessToAll.anacondaPath}");


            try
            {
                AccessToAll.condaEnvName = _condaEnvName;
            }
            catch (ArgumentException e)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                return;
            }
            AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, $"\"{AccessToAll.condaEnvName}\" is a valid anaconda environment");


            try
            {
                AccessToAll.pythonDllName = _pythonDllName;
            }
            catch (ArgumentException e)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                return;
            }
            AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, $"{AccessToAll.pythonDllName} is a valid .dll file");


            #endregion Check Data


            //3) Initialize Python.NET, following https://github.com/pythonnet/pythonnet/wiki/Using-Python.NET-with-Virtual-Environments
            var condaEnvPath = AccessToAll.condaEnvPath;
            var pythonDllPath = AccessToAll.pythonDllPath;
            var pythonProjectDirectory = AccessToAll.pythonProjectDirectory;
            
            string Lib = Path.Combine(condaEnvPath, "Lib");
            string site_packages = Path.Combine(Lib, "site-packages");
            string DLLs = Path.Combine(condaEnvPath, "DLLs");

            if (start && AccessToAll.hasPythonStarted)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python.NET is already started.");
                return;
            }
            if (start && !AccessToAll.hasPythonStarted) 
            {
                var path = Environment.GetEnvironmentVariable("PATH").TrimEnd(';');
                if (!path.Contains(condaEnvPath))
                {
                    path = string.IsNullOrEmpty(path) ? condaEnvPath : path + ";" + condaEnvPath; //add condaEnvPath to PATH (only once)
                }
                Environment.SetEnvironmentVariable("PATH", path, EnvironmentVariableTarget.Process);
                Environment.SetEnvironmentVariable("PYTHONHOME", condaEnvPath, EnvironmentVariableTarget.Process);
                Environment.SetEnvironmentVariable("PYTHONPATH", $"{site_packages};{Lib};{DLLs};{pythonProjectDirectory}", EnvironmentVariableTarget.Process);

                //Runtime.PythonDLL = pythonDllPath;
                Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", pythonDllPath);

                PythonEngine.PythonHome = condaEnvPath;
                PythonEngine.PythonPath = Environment.GetEnvironmentVariable("PYTHONPATH", EnvironmentVariableTarget.Process);

                PythonEngine.Initialize();
                AccessToAll.hasPythonStarted = true;

                var m_threadState = PythonEngine.BeginAllowThreads();
                using (Py.GIL())
                {
                    dynamic np = Py.Import("numpy");
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "Python.NET setup completed.");
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, $"According to Numpy, cos(2*pi)= {np.cos(np.pi * 2)}");
                }
                PythonEngine.EndAllowThreads(m_threadState);
            }

            if (!start)
            {
                ClosePythonEngine();
            }
            if (!AccessToAll.hasPythonStarted)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, $"Python.NET is closed. Please restart Python.NET.");
            }

        }

        /// <summary>
        /// When Grasshopper is closed, stop the pythonManager
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="doc"></param>
        private void DocumentClose(GH_DocumentServer sender, GH_Document doc)
        {
            ClosePythonEngine();
        }
        private void ClosePythonEngine()
        {
            if (!AccessToAll.hasPythonStarted) //Python has not been started
            {
                return; //nothing to do
            }
            //else Python has been started and must be closed
            try
            {
                PythonEngine.Shutdown();
            }
            catch (Exception e)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, $"Python.NET closed with this error message: {e.Message}");
            }
            AccessToAll.hasPythonStarted = false;
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
            get { return new Guid("b291cfe2-587e-4274-b05b-997ed2cb067a"); }
        }





    }

}
