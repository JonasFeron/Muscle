       
    public static class AppConfig
    {


    }
       
       

        
        /// <summary>
        /// Checks the user input for validity and sets the configuration accordingly.
        /// </summary>
        /// <param name="_anacondaPath">The path to the Anaconda installation directory.</param>
        public static void TryConfiguringAnacondaPath(string _anacondaPath)
        {
            //anacondaPath
            try
            {
                AnacondaPath = _anacondaPath;
            }
            catch (ArgumentException e)
            {
                string default_msg = $"Please provide a valid path, similar to: {InvalidAnacondaPath }";
                
                if (_anacondaPath == InvalidAnacondaPath)
                {
                    throw new ArgumentException($"Impossible to find a valid Anaconda3 Installation. " + default_msg);
                }
                else
                {
                    // error message = "The specified path does not contain a valid Anaconda3 installation. Please provide a valid path, similar to: C:\\Users\\Me\\anaconda3"
                    throw new ArgumentException(e.Message, default_msg);
                }
            }
        }
        

        public static void TryConfiguringCondaEnv(string _condaEnvName)
        {
            //condaEnvName
            try
            {
                CondaEnvName = _condaEnvName;
            }
            catch (Exception)
            {
                throw;
            }
        }

        public static void TryConfiguringPythonDllName(string _pythonDllName)
        {
            //pythonDllName
            try
            {
                PythonDllName = _pythonDllName;
            }
            catch (Exception)
            {
                throw;
            }
        }
                public static string DefaultAnacondaPath
        {
            get
            {
                if (!string.IsNullOrEmpty(PythonNETConfig.AnacondaPath))
                {
                    return PythonNETConfig.AnacondaPath;
                }
                else
                {
                    return PythonNETConfig.InvalidAnacondaPath;
                }
            }
        }
        /// <summary>
        /// Checks the user input for validity and sets the configuration accordingly.
        /// </summary>
        /// <param name="_anacondaPath">The path to the Anaconda installation directory.</param>
        /// <param name="_condaEnvName">The name of the conda environment to activate.</param>
        /// <param name="_pythonDllName">The name of the python DLL file.</param>
        public static void TryConfiguring(string _anacondaPath, string _condaEnvName, string _pythonDllName)
        {
            //anacondaPath
            try
            {
                PythonNETConfig.TryConfiguringAnacondaPath(_anacondaPath);
                ValidAnacondaPath = true;
            }
            catch (Exception)
            {
                ValidAnacondaPath = false;
                throw;
            }

            //condaEnvName
            try
            {
                PythonNETConfig.TryConfiguringCondaEnvName(_condaEnvName);
                ValidCondaEnvName = true;
            }
            catch (Exception)
            {
                ValidCondaEnvName = false;
                throw;
            }

            //pythonDllName
            try
            {
                PythonNETConfig.TryConfiguringPythonDllName(_pythonDllName);
                ValidPythonDllName = true;
            }
            catch (Exception)
            {
                ValidPythonDllName = false;
                throw;
            }
        }
