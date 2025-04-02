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

using System;
using System.IO;
using Python.Runtime;
using MuscleCore.Converters;
using MuscleCore.Solvers;

namespace MuscleCore.PythonNETInit
{
    public static class PythonNETManager
    {
        public static readonly string MusclePy = "musclepy";
        public static bool IsInitialized { get; private set; } = false;

        private static bool UserMode { get; set; } = false;


        #region Launch


        public static void Launch(PythonNETConfig config)
        {
            if (!config.IsValid)
            {
                throw new ArgumentException("The provided configuration is not valid.");
            }

            // in user mode, the user is supposed to have run "pip install musclepy"
            // which means that musclepy will be found from the conda environment.
            // hence, the source directory of musclepy is null in user mode.
            // in developer mode, the source directory of musclepy is the path to "musclepy" source code.
            UserMode = string.IsNullOrEmpty(config.SrcDirectory);

            IsInitialized = Initialize(config.CondaEnvPath, config.PythonDllName, config.SrcDirectory);
        }

        /// <summary>
        /// Initializes the Python engine. This method must be called before using any methods from the Python.Runtime namespace.
        /// </summary>
        /// <param name="condaEnvPath">The path to the conda environment where Python is installed.</param>
        /// <param name="pythonDllName">The Name of the python3xx.dll file contained in the conda environment.</param>
        /// <param name="srcDirectory">The path to the directory containing the python package (developer mode), or null (user mode).</param>
        /// <remarks>
        /// This method sets the following environment variables:
        /// PATH: adds condaEnvPath to PATH
        /// PYTHONHOME: sets to condaEnvPath
        /// PYTHONPATH: sets to the concat of site_packages, Lib, DLLs and srcDirectory
        /// PYTHONNET_PYDLL: sets to pythonDllPath
        /// </remarks>
        private static bool Initialize(string condaEnvPath, string pythonDllName, string srcDirectory = null)
        {
            if (IsInitialized)
            {
                return true; //nothing to do
            }
            try
            {
                string Lib = Path.Combine(condaEnvPath, "Lib");
                string site_packages = Path.Combine(Lib, "site-packages");
                string DLLs = Path.Combine(condaEnvPath, "DLLs");
                string pythonDllPath = Path.Combine(condaEnvPath, pythonDllName);

                var path = Environment.GetEnvironmentVariable("PATH")?.TrimEnd(';') ?? string.Empty;
                if (!path.Contains(condaEnvPath))
                {
                    path = string.IsNullOrEmpty(path) ? condaEnvPath : path + ";" + condaEnvPath; //add condaEnvPath to PATH (only once)
                }

                Environment.SetEnvironmentVariable("PATH", path, EnvironmentVariableTarget.Process);
                Environment.SetEnvironmentVariable("PYTHONHOME", condaEnvPath, EnvironmentVariableTarget.Process);
                
                if (UserMode)//user mode
                {
                    //in user mode, musclepy will be accessible from site_packages, supposing the user has already run "pip install musclepy"
                    Environment.SetEnvironmentVariable("PYTHONPATH", $"{site_packages};{Lib};{DLLs}", EnvironmentVariableTarget.Process);

                }
                else  //developer mode
                {
                    //in developer mode, musclepy will be accessible from the srcDirectory
                    Environment.SetEnvironmentVariable("PYTHONPATH", $"{site_packages};{Lib};{DLLs};{srcDirectory}", EnvironmentVariableTarget.Process);
                }
                
                //Runtime.PythonDLL = pythonDllPath;
                Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", pythonDllName);

                PythonEngine.PythonHome = condaEnvPath;
                PythonEngine.PythonPath = Environment.GetEnvironmentVariable("PYTHONPATH", EnvironmentVariableTarget.Process) ?? string.Empty;

                PythonEngine.Initialize();
                Main.RegisterConverters();

                TryPythonEngine(srcDirectory, site_packages);
                
                return true;
            }
            catch (Exception)
            {
                throw;
            }
        }
        #endregion Launch

        #region ShutDown
        /// <summary>
        /// Shuts down the Python engine if it is initialized.
        /// </summary>
        public static void ShutDown()
        {
            if (!IsInitialized)
            {
                return; //nothing to do
            }
            //else Python is initialized and must be closed
            try
            {
                IsInitialized = !KillInitialization();
            }
            catch (Exception)
            {
                throw;
            }
        }
        private static bool KillInitialization()
        {
            PythonEngine.Shutdown();
            Environment.SetEnvironmentVariable("PYTHONHOME", string.Empty, EnvironmentVariableTarget.Process);
            Environment.SetEnvironmentVariable("PYTHONPATH", string.Empty, EnvironmentVariableTarget.Process);
            Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", string.Empty, EnvironmentVariableTarget.Process);
            return true;
        }
        #endregion ShutDown




        #region Test
        private static void TryPythonEngine(string srcDirectory, string site_packages)
        {
            // Validate MusclePy installation
            TryFindingMusclePyInstallation(srcDirectory, site_packages);

            // Validate Python.NET initialization by testing cos(pi*2) == 1
            TestPythonEngine();
                                
            // Test MusclePy test script
            TestMusclePy();
        }
                


        /// <summary>
        /// Validates that MusclePy is properly installed either in the source directory or site-packages.
        /// </summary>
        /// <param name="srcDirectory">The source directory path.</param>
        /// <param name="site_packages">The site-packages directory path.</param>
        /// <exception cref="InvalidOperationException">Thrown when MusclePy is not found.</exception>
        private static void TryFindingMusclePyInstallation(string srcDirectory, string site_packages)
        {
            bool musclepyFound = false;

            if (string.IsNullOrEmpty(srcDirectory)) //user mode
            {
                // Check if MusclePy directory exists in site-packages
                string musclepyPath = Path.Combine(site_packages, MusclePy);
                if (Directory.Exists(musclepyPath))
                {
                    musclepyFound = true;
                }
            }
            else //developer mode
            {
                string srcMusclePyPath = Path.Combine(srcDirectory, MusclePy);
                if (Directory.Exists(srcMusclePyPath))
                {
                    musclepyFound = true;
                }
            }
            if (!musclepyFound)
            {
                throw new InvalidOperationException("musclepy is not installed in this anaconda environment. Please choose a valid anaconda environment or run the command 'pip install musclepy' in the anaconda prompt.");
            }

            // Check if MusclePy can be imported from C#
            var m_threadState = PythonEngine.BeginAllowThreads();
            try
            {
                using (Py.GIL())
                {
                    dynamic musclepy = Py.Import(MusclePy);
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Failed to import musclepy from C#", ex);
            }
            finally
            {
                PythonEngine.EndAllowThreads(m_threadState);
            }
        }


        /// <summary>
        /// Tests if Python.NET is correctly initialized by verifying that cos(pi*2) equals 1.
        /// </summary>
        /// <exception cref="InvalidOperationException">Thrown when the test fails.</exception>
        private static void TestPythonEngine()
        {
            try
            {
                var m_threadState = PythonEngine.BeginAllowThreads();
                try
                {
                    using (Py.GIL())
                    {
                        dynamic np = Py.Import("numpy");
                        double cosValue = np.cos(np.pi * 2);
                        
                        // Check if the value is approximately equal to 1
                        if (Math.Abs(cosValue - 1.0) > 1e-10)
                        {
                            throw new InvalidOperationException($"Python.NET initialization test failed: cos(2*pi) = {cosValue} ≠ 1");
                        }
                    }
                }
                catch (Exception ex)
                {
                    throw new InvalidOperationException("Failed to import numpy from Python", ex);
                }
                finally
                {
                    PythonEngine.EndAllowThreads(m_threadState);
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Python.NET is not correctly initialized", ex);
            }
        }


        private static void TestMusclePy()
        {
            // Arrange
            string str0 = "HELLO";
            string str1 = "from python";

            try
            {
                string? result = TestScriptSolver.Solve(str0, str1);

                // Validate
                if (result == null)
                {
                    throw new InvalidOperationException("MusclePy test failed: result is null");
                }
                
                if (result != "hello FROM PYTHON")
                {
                    throw new InvalidOperationException($"MusclePy test failed: expected 'hello FROM PYTHON', got '{result}'");
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Failed to validate MusclePy installation", ex);
            }
        }
        #endregion Test
    }
}