using MuscleCore.PythonNETInit;

namespace MuscleApp.PythonNETInit
{
    public static class PythonNET 
    {

        #region Invalid Configuration
        // value to display in case of invalid configuration
        public static readonly string InvalidAnacondaPath = @"C:\Users\Me\Anaconda3";
        public static readonly string InvalidPythonDllName = @"python3xx.dll";
        #endregion Invalid Configuration


        #region Default Configuration
        public static bool ValidDefaultAnacondaPath { get; private set;} = false;
        public static string DefaultAnacondaPath { 
            get
            {
                string foundAnacondaInstallation = PythonNETConfig.TryFindingAnaconda();
                if (!string.IsNullOrEmpty(foundAnacondaInstallation))
                {
                    ValidDefaultAnacondaPath = true;
                    return foundAnacondaInstallation;
                }
                else
                {
                    ValidDefaultAnacondaPath = false;
                    return InvalidAnacondaPath;
                }
            }
        }
        private static readonly string _usualCondaEnvName = "muscle"; // conda environment where musclepy should have been 'pip install musclepy'

        public static string DefaultCondaEnvName{
            get
            {
                // if default anaconda path is invalid, return "muscle" eventhough it may not exist
                if (!ValidDefaultAnacondaPath)
                {
                    return _usualCondaEnvName;
                }
                // if "muscle" is a valid conda environment name, return it
                if (PythonNETConfig.IsValidCondaEnvName(DefaultAnacondaPath, _usualCondaEnvName))
                {
                    return _usualCondaEnvName;
                }
                // if "muscle" is not a valid conda environment name, return "base"
                return PythonNETConfig.BASECondaEnv;
            }
        }

        public static string DefaultPythonDllName { 
            get
            {
                // if default anaconda path is invalid, return "python3xx.dll" eventhough it does not exist
                if (!ValidDefaultAnacondaPath)
                {
                    return InvalidPythonDllName;
                }
                // try to find the Python DLL file for the default conda environment
                string? condaEnvPath = PythonNETConfig.BuildCondaEnvPath(DefaultAnacondaPath, DefaultCondaEnvName);
                string? pythonDllName = PythonNETConfig.TryFindingPythonDll(condaEnvPath);

                if (string.IsNullOrEmpty(pythonDllName))
                {
                    return InvalidPythonDllName;
                }
                return pythonDllName;
            }
        }
        #endregion Default Configuration

        #region Developer mode
        public static bool DeveloperMode {get; private set; } = false;  // will be set to true in the CheckIfDeveloperMode Method if userConfig.CondaEnvName == "muscle4developers"
        public static readonly string CondaEnvName4Developers = "muscle4developers"; // Password to switch from user mode to developer mode from Rhino

        /// <summary>
        /// In Developer mode, gets the full path to the source directory where musclepy is located.
        /// The current directory of "Muscle.gha"is expected to be within the build output path (e.g., .../src/Muscle/bin/Debug/net48/).
        /// Navigating four levels up from the current directory allows to find //.../src/musclepy for Python.NET initialization.
        /// In User mode, MusclePy is expected to be installed in the conda environment. -> srcDirectory is useless. 
        /// </summary>
        private static string srcDirectory
        {
            get
            {
                var currentDirectory = Directory.GetCurrentDirectory(); //.../src/Muscle/bin/Debug/net48/
                var src = Path.GetFullPath(Path.Combine(currentDirectory, "..", "..", "..","..","MusclePy")); //.../src/MusclePy/
                return src;
            }
        }

        //check if Developer mode
        private static string CheckIfDeveloperMode(string condaEnvName)
        {
            if (condaEnvName == CondaEnvName4Developers) //name of the conda environment signaling developer mode
            {
                DeveloperMode = true;
                return "base"; //activate an environment of your choice instead
            }
            // else user mode
            DeveloperMode = false;
            return condaEnvName; //return the original conda environment name
        }
        #endregion Developer mode


        #region User Configuration
        public static PythonNETConfig? UserConfig    {get; private set;} = null;
        public static bool TryConfiguring(string anacondaPath, string condaEnvName, string pythonDllName)
        {
            bool success = false;
            condaEnvName = CheckIfDeveloperMode(condaEnvName);
            string srcDir = string.Empty;

            if (DeveloperMode)
            {
                // import musclepy from src directory
                // get path to musclepy src directory from this application Muscle.gha
                srcDir = srcDirectory;
            }
            // else user mode: condaEnvName is unchanged and srcDir is empty

            try
            {
                UserConfig = new PythonNETConfig(anacondaPath, condaEnvName, pythonDllName, srcDir);
                success = true;
            }
            catch(Exception)
            {
                throw;
            }
            return success;   
        }
        #endregion User Configuration


        #region PythonNetManager
        public static void Launch(PythonNETConfig config)
        {
            try
            {
                PythonNETManager.Launch(config);
            }
            catch(Exception)
            {
                throw;
            }
        }
        public static bool IsInitialized { get { return PythonNETManager.IsInitialized; } }

        public static void ShutDown()
        {
            try
            {
                PythonNETManager.ShutDown();
            }
            catch(Exception)
            {
                throw;
            }
        }
        #endregion PythonNetManager
    }
} 

        