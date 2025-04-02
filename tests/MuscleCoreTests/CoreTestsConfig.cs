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

using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MuscleCore.PythonNETInit;


namespace MuscleCoreTests
{
    public static class CoreTestsConfig
    {


        private static bool _developerMode = false; //choose whether Testing in developer mode or user mode

        private static string _condaEnvName = "muscledebug"; // for testing as a user, set the name of the conda environment where you have 'pip install musclepy'

        private static string _anacondaPath = PythonNETConfig.TryFindingAnaconda(); // path to Anaconda if found

        private static string _pythonDllName = string.Empty; // let PythonNETConfig find the Python DLL file for the test conda environment

        public static PythonNETConfig testConfig
        {

            get
            {

                if (_developerMode)
                {
                    // import musclepy from src directory
                    // get path to musclepy src directory from this Test application
                    string srcDir = Path.GetFullPath(Path.Combine(
                                                            Directory.GetCurrentDirectory(),
                                                            "..", "..", "..", "..", "..", "src"));

                    return new PythonNETConfig(_anacondaPath, "base", _pythonDllName, srcDir);

                }
                else //user mode
                {
                    string srcDir = string.Empty; // reset src dir where musclepy source code can be found
                    return new PythonNETConfig(_anacondaPath, _condaEnvName, _pythonDllName, srcDir);
                }
            }
        }
    }
}