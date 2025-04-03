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
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace MuscleCore.PythonNETInit
{

    public class PythonNETConfig
    {
        public static readonly string BASECondaEnv = "base"; // base conda environment - which always exists

        #region Basic Properties
        // to configure PythonNET, we need to set valid _anacondaPath, _condaEnvName, _pythonDllName and _srcDir. 
        // _anacondaPath is the path to the Anaconda installation directory.
        // _condaEnvName is the name of the conda environment where specific python version and packages are installed.
        // _pythonDllName is the name of the Python DLL file, specifing the version of Python to use.
        // _srcDir is the path to MusclePy source code, in case working as a developer, null otherwise.
        private string _anacondaPath = string.Empty;
        private string _condaEnvName = BASECondaEnv;
        private string _pythonDllName = string.Empty;
        private string _srcDir = string.Empty;


        public bool IsValid {
            get
            {
                // Use property getters instead of method calls
                bool validAnaconda = this.HasValidAnacondaPath;
                bool validCondaEnv = this.HasValidCondaEnvPath;
                bool validPythonDll = this.HasValidPythonDllName;
                return validAnaconda && validCondaEnv && validPythonDll;
            }
        }

        public string SrcDirectory
        {
            get
            {
                return _srcDir;
            }
            set
            {
                _srcDir = value;
            }
        }
        


        #region Constructors

        /// <summary>
        /// Default constructor of the <see cref="PythonNETConfig"/> class.
        /// </summary>
        public PythonNETConfig()
        {
            AnacondaPath = TryFindingAnaconda();
            CondaEnvName = BASECondaEnv;
            PythonDllName = TryFindingPythonDll(this.CondaEnvPath);
            SrcDirectory = string.Empty;
        }

        /// <summary>
        /// Constructor of the <see cref="PythonNETConfig"/> class.
        /// </summary>
        /// <param name="anacondaPath">The path to the Anaconda installation directory.</param>
        /// <param name="condaEnvName">The name of the conda environment where specific Python version and packages are installed. Defaults to <see cref="BASECondaEnv"/>.</param>
        /// <param name="srcDir">The path to MusclePy source code, in case working as a developer. Defaults to <see cref="string.Empty"/>.</param>
        /// <param name="pythonDllName">The name of the Python DLL file, specifying the version of Python to use. Defaults to <see cref="InvalidPythonDllName"/>.</param>
        public PythonNETConfig(string anacondaPath, string condaEnvName, string pythonDllName, string srcDir)
        {
            try
            {
                AnacondaPath = anacondaPath; 
            }
            catch (Exception e1)
            {
                try
                {
                    AnacondaPath = TryFindingAnaconda();
                }
                catch (Exception)
                {
                    throw new ArgumentException($"{e1.Message} Please check that Anaconda is installed and provide a valid path.");
                }
            }

            try
            {
                CondaEnvName = condaEnvName;
            }
            catch (Exception)
            {
                throw;
            }


            try
            {
                PythonDllName = pythonDllName; 
            }
            catch (Exception) // neglect this exception and try to find the Python DLL
            {
                try
                {
                    PythonDllName = TryFindingPythonDll(this.CondaEnvPath);
                }
                catch (Exception)
                {
                    throw; 
                }
            }

            SrcDirectory = srcDir;
        }

        #endregion Constructors
        #region Anaconda Path
        
        /// <summary>
        /// Gets or sets the path to the Anaconda installation directory.
        /// </summary>
        /// <remarks>
        /// This property checks for the existence of Anaconda in two possible locations:
        /// 1. The user's profile directory (e.g., "C:\Users\Me\Anaconda3")
        /// 2. The ProgramData directory (e.g., "C:\ProgramData\Anaconda3")
        /// If Anaconda is found in either location, the path is returned. Otherwise, null is returned.
        /// </remarks>
        public string? AnacondaPath
        {
            get
            {
                return _anacondaPath;
            }
            set
            {
                if (!IsValidAnacondaPath(value))
                {
                    throw new ArgumentException($"{value} is not a valid Anaconda3 installation.");
                }
                else
                {
                    _anacondaPath = value ?? string.Empty;
                }
            }
        }

        public bool HasValidAnacondaPath {
            get
            {
                return !string.IsNullOrEmpty(_anacondaPath);
            }
        }
        
        /// <summary>
        /// Checks whether the given path is a valid Anaconda3 installation directory.
        /// </summary>
        /// <param name="anacondaPath">The path to check.</param>
        /// <returns>
        /// <c>true</c> if the path is a valid Anaconda3 installation directory, <c>false</c> otherwise.
        /// </returns>
        private static bool IsValidAnacondaPath(string? anacondaPath)
        {
            if (string.IsNullOrEmpty(anacondaPath)
                || !Directory.Exists(anacondaPath) 
                //|| !anacondaPath.EndsWith("anaconda3", StringComparison.OrdinalIgnoreCase)
                || !File.Exists(Path.Combine(anacondaPath, "python.exe")))
            {
                return false;
            }
            return true;
        }

        /// <summary>
        /// Tries to find a valid Anaconda3 installation in one of two possible locations:
        /// 1. The user's profile directory (e.g., "C:\Users\Me\Anaconda3")
        /// 2. The ProgramData directory (e.g., "C:\ProgramData\Anaconda3")
        /// If Anaconda is found in either location, the path is returned. Otherwise, returns an empty string.
        /// </summary>
        public static string TryFindingAnaconda() 
        { 
            string[] possiblePaths = {
                    Path.Combine(Environment.GetFolderPath(Environment.SpecialFolder.UserProfile), "Anaconda3"), // "C:\Users\Me\Anaconda3"
                    @"C:\ProgramData\Anaconda3"
            };
            
            foreach (var path in possiblePaths)
            {
                if (IsValidAnacondaPath(path))
                {
                    return path;
                }
            }
            return string.Empty;
        }
        #endregion Anaconda Path
        

        #region Conda Environment

        /// <summary>
        /// Gets or sets the name of the conda environment.
        /// </summary>
        public string CondaEnvName
        {
            get
            {
                return _condaEnvName;
            }
            set
            {
                if (!IsValidCondaEnvName(this.AnacondaPath, value))
                {
                    throw new ArgumentException($"{value} is not a valid conda environment name. Please provide a conda environment name containing a valid python.exe.");
                }
                _condaEnvName = value;
                _condaEnvPath = BuildCondaEnvPath(this.AnacondaPath, value) ?? string.Empty;
            }
        }
        public static bool IsValidCondaEnvName(string? anacondaPath, string? condaEnvName)
        {
            if (!IsValidAnacondaPath(anacondaPath))
            {
                return false;
            }
            string? condaEnvPath = BuildCondaEnvPath(anacondaPath,condaEnvName);            
            if (string.IsNullOrEmpty(condaEnvPath) || !File.Exists(Path.Combine(condaEnvPath, "python.exe")))
            {
                return false;
            }
            return true;
        }

        private string _condaEnvPath = string.Empty;

        /// <summary>
        /// Gets the path to the conda environment.
        /// </summary>
        public string CondaEnvPath
        {
            get
            {
                return _condaEnvPath;
            }
        }
        
        public static string? BuildCondaEnvPath(string? anacondaPath, string? condaEnvName)
        {
            if (string.IsNullOrEmpty(anacondaPath) || string.IsNullOrEmpty(condaEnvName))
            {
                return string.Empty;
            }
            if (condaEnvName == BASECondaEnv)
            {
                return anacondaPath;
            }
            else
            {
                return Path.Combine(anacondaPath, "envs", condaEnvName);
            }
        }

        /// <summary>
        /// Gets a value indicating whether the conda environment path is valid.
        /// </summary>
        public bool HasValidCondaEnvPath {
            get
            {
                return !string.IsNullOrEmpty(_condaEnvPath);
            }
        }

        #endregion Conda Environment

        #region Python DLL Name

        /// <summary>
        /// Returns a valid Python DLL in the specified conda environment if it finds it, otherwise returns an empty string.
        /// </summary>
        public static string? TryFindingPythonDll(string? condaEnvPath) 
        { 
            if (string.IsNullOrEmpty(condaEnvPath))
            {
                return string.Empty;
            }

            string[] possibleNames = { "python319.dll", "python318.dll", "python317.dll", "python316.dll", "python315.dll", "python314.dll", "python313.dll", "python312.dll", "python311.dll", "python310.dll", "python39.dll", "python38.dll", "python37.dll", "python36.dll", "python35.dll", "python34.dll", "python33.dll", "python32.dll", "python31.dll" };
            foreach (var name in possibleNames)
            {
                if (IsValidPythonDllName(condaEnvPath, name))
                {
                    return name;
                }
            }
            return string.Empty;
        }

        /// <summary>
        /// Gets or sets the name of the Python DLL file.
        /// </summary>
        public string? PythonDllName
        {
            get
            {
                return _pythonDllName;
            }
            set
            {
                string condaEnvPath = this.CondaEnvPath;
                if (string.IsNullOrEmpty(value) || !IsValidPythonDllName(condaEnvPath, value))
                {
                    throw new ArgumentException($"{value} does not exist in the specified Anaconda environment. Please check that a \"python3xx.dll\" file exists in {CondaEnvPath}.");
                }
                _pythonDllName = value ?? string.Empty;
            }
        }

        private static bool IsValidPythonDllName(string? condaEnvPath, string? pythonDllName)
        {
            if (string.IsNullOrEmpty(pythonDllName) || string.IsNullOrEmpty(condaEnvPath))
            {
                return false;
            }
            return File.Exists(Path.Combine(condaEnvPath, pythonDllName));
        }
        
        public bool HasValidPythonDllName {
            get
            {
                return !string.IsNullOrEmpty(_pythonDllName);
            }
        }



        #endregion Python DLL Name

    }
}

#endregion
