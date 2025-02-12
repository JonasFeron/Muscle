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
using PythonConnect;
using log4net.Core;
using System.IO;

namespace MyGrasshopperPlugIn.PythonInitComponents
{
    public class StartPythonComponent : GH_Component
    {
        #region Properties
        private static readonly Level[] _validLogLevels = { Level.Off, Level.Fatal, Level.Error, Level.Warn, Level.Info, Level.Debug };
        private static readonly int[] _logLevelValues = { Level.Off.Value, Level.Fatal.Value, Level.Error.Value, Level.Warn.Value, Level.Info.Value, Level.Debug.Value };
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

        private static readonly int default_logLvl = Level.Off.Value;
        private static readonly double default_timeout = 10;


        #endregion Properties

        public StartPythonComponent()
          : base("StartPythonComponent", "StartPy",
              "Initialize Python before running any calculation", AccessToAll.GHAssemblyName, AccessToAll.GHComponentsFolder0)
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
            pManager.AddIntegerParameter("Level", "lvl", "Level of messages in the Log file for debuging: choose the level from the provided list (right click).", GH_ParamAccess.item, default_logLvl);
            pManager[2].Optional = true;
            pManager.AddNumberParameter("TimeOut", "timeout", "This is the time (in seconds) a python script will be allowed to run before it is aborted.", GH_ParamAccess.item, default_timeout);
            pManager[3].Optional = true;
            pManager.AddTextParameter("conda Environment Name", "condaEnv", "Name of the conda environment to activate.", GH_ParamAccess.item, default_condaEnvName);
            pManager[4].Optional = true;
            pManager.AddTextParameter("Anaconda Directory", "condaPath", "Path to the directory where Anaconda3 is installed.", GH_ParamAccess.item, default_anacondaPath);
            pManager[5].Optional = true;

            var levels = pManager[2] as Grasshopper.Kernel.Parameters.Param_Integer;
            foreach (var level in _validLogLevels)
            {
                levels.AddNamedValue(level.DisplayName, level.Value);
            }
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
            int logLvl = default_logLvl;
            double timeout = default_timeout;
            string _condaEnvName = default_condaEnvName;
            string _anacondaPath = default_anacondaPath;


            if (!DA.GetData(0, ref start)) return;
            if (!DA.GetData(1, ref _user_mode)) return;
            if (!DA.GetData(2, ref logLvl)) return;
            if (!DA.GetData(3, ref timeout)) return;
            if (!DA.GetData(4, ref _condaEnvName)) return;
            if (!DA.GetData(5, ref _anacondaPath)) return;


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

            if (AccessToAll.activateCondaEnvScript == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Please ensure that the file \"activateCondaEnv.bat\" is located in: {AccessToAll.pythonProjectDirectory}");
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


            int index = Array.IndexOf(_logLevelValues, logLvl);
            if (index == -1)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, $"Please choose a valid LogLevel from the provided input list");
                logLvl = default_logLvl;
                index = Array.IndexOf(_logLevelValues, logLvl);
            }
            Level currentLevel = _validLogLevels[index];


            if (timeout <= 0)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "Timeout must be greater than 0");
                timeout = 10;
            }
            int timeout_ms = Convert.ToInt32(timeout * 1000);

            #endregion Check Data


            //3) Initialize Python (and log4net for debugging)

            if (start && AccessToAll.pythonManager != null) //already started
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "There is already one Anaconda ready to perform on the Canvas.");
                return;
            }

            if (start && AccessToAll.pythonManager == null) //start Anaconda
            {

                // Set up the logger with a desired level
                LogHelper.Setup(currentLevel.DisplayName, AccessToAll.tempDirectory);
                var log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

                // Start Anaconda
                PythonManager.Setup(AccessToAll.pythonProjectDirectory, AccessToAll.condaActivateScript, AccessToAll.condaEnvName, timeout_ms);

                AccessToAll.pythonManager = PythonManager.Instance; //Initialize a python Thread

                if (AccessToAll.pythonManager != null)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "Anaconda is ready to perform.");
                }
                else
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to start Anaconda.");
                    foreach (string errorMessage in PythonManager.GetErrorMessages())
                    {
                        AddRuntimeMessage(GH_RuntimeMessageLevel.Error, errorMessage);
                    }
                }
                return;
            }

            if (!start) //stop Anaconda
            {
                ClosePythonManager();
            }

            if (AccessToAll.pythonManager == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Anaconda stopped. Please relaunch it.");
                return;
            }
        }

        /// <summary>
        /// When Grasshopper is closed, stop the pythonManager
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="doc"></param>
        private void DocumentClose(GH_DocumentServer sender, GH_Document doc)
        {
            ClosePythonManager();
        }
        private void ClosePythonManager()
        {
            if (AccessToAll.pythonManager != null)
            {
                AccessToAll.pythonManager.Dispose();
                AccessToAll.pythonManager = null;
            }
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
            get { return new Guid("e2fe9063-2b08-4b68-9e43-bd38e3abad1b"); }
        }





    }

}
