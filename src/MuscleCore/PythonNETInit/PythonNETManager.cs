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
//------------------------------------------------------------------------------------------------------------

using System;
using System.IO;
using Python.Runtime;
using MuscleCore.Converters;
using MuscleCore.Solvers;

namespace MuscleCore.PythonNETInit
{
    public static class PythonNETManager
    {
        public static bool IsInitialized { get; set; } = false;

        /// <summary>
        /// Initializes the Python engine. This method must be called before using any methods from the Python.Runtime namespace.
        /// </summary>
        /// <param name="condaEnvPath">The path to the conda environment where Python is installed.</param>
        /// <param name="pythonDllName">The Name of the python3xx.dll file contained in the conda environment.</param>
        /// <param name="srcDirectory">The path to the directory containing the python package.</param>
        /// <remarks>
        /// This method sets the following environment variables:
        /// PATH: adds condaEnvPath to PATH
        /// PYTHONHOME: sets to condaEnvPath
        /// PYTHONPATH: sets to the concat of site_packages, Lib, DLLs and srcDirectory
        /// PYTHONNET_PYDLL: sets to pythonDllPath
        /// </remarks>
        public static void Initialize(string condaEnvPath, string pythonDllName, string srcDirectory)
        {
            if (IsInitialized)
            {
                return; //nothing to do
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
                Environment.SetEnvironmentVariable("PYTHONPATH", $"{site_packages};{Lib};{DLLs};{srcDirectory}", EnvironmentVariableTarget.Process);
                //in development mode, MusclePy will be accessible from the srcDirectory
                //in user mode, MusclePy will be accessible from site_packages, supposing the user will first "pip install MusclePy"

                //Runtime.PythonDLL = pythonDllPath;
                Environment.SetEnvironmentVariable("PYTHONNET_PYDLL", pythonDllName);

                PythonEngine.PythonHome = condaEnvPath;
                PythonEngine.PythonPath = Environment.GetEnvironmentVariable("PYTHONPATH", EnvironmentVariableTarget.Process) ?? string.Empty;

                PythonEngine.Initialize();
                Main.RegisterConverters();
                
                // Validate Python.NET initialization by testing cos(pi*2) == 1
                TestPythonEngine();
                
                // Validate MusclePy installation
                ValidateMusclePyInstallation(srcDirectory, site_packages);
                
                // Test MusclePy functionality
                TestMusclePy();
                
                IsInitialized = true;
                return;
            }
            catch (Exception)
            {
                throw;
            }
        }

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
                PythonEngine.Shutdown();
                IsInitialized = false;
            }
            catch (Exception)
            {
                throw;
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

        /// <summary>
        /// Validates that MusclePy is properly installed either in the source directory or site-packages.
        /// </summary>
        /// <param name="srcDirectory">The source directory path.</param>
        /// <param name="site_packages">The site-packages directory path.</param>
        /// <exception cref="InvalidOperationException">Thrown when MusclePy is not found.</exception>
        private static void ValidateMusclePyInstallation(string srcDirectory, string site_packages)
        {
            try
            {
                var m_threadState = PythonEngine.BeginAllowThreads();
                try
                {
                    using (Py.GIL())
                    {
                        bool musclePyFound = false;
                        
                        // Try to import MusclePy
                        try
                        {
                            dynamic musclePy = Py.Import("MusclePy");
                            musclePyFound = true;
                        }
                        catch (PythonException)
                        {
                            // Check if MusclePy directory exists in srcDirectory
                            string srcMusclePyPath = Path.Combine(srcDirectory, "MusclePy");
                            if (Directory.Exists(srcMusclePyPath))
                            {
                                musclePyFound = true;
                            }
                            
                            // Check if MusclePy directory exists in site_packages
                            string sitePackagesMusclePyPath = Path.Combine(site_packages, "MusclePy");
                            if (Directory.Exists(sitePackagesMusclePyPath))
                            {
                                musclePyFound = true;
                            }
                        }
                        
                        if (!musclePyFound)
                        {
                            throw new InvalidOperationException(
                                "MusclePy is not correctly installed. " +
                                "In user mode, please run 'pip install MusclePy' in your conda environment first.");
                        }
                    }
                }
                finally
                {
                    PythonEngine.EndAllowThreads(m_threadState);
                }
            }
            catch (Exception ex)
            {
                throw new InvalidOperationException("Failed to validate MusclePy installation", ex);
            }
        }
        private static void TestMusclePy()
        {
            // Arrange
            string str0 = "HELLO";
            string str1 = "from python";

            try
            {
                string result = TestScriptSolver.Solve(str0, str1);

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

    }
}