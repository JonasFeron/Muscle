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
using Grasshopper.Kernel;

namespace Muscle.Components
{
    public static class GHComponentsFolders
    {

        private static MuscleInfo info = new MuscleInfo();

        public static string GHAssemblyName // "Muscle"
        {
            get
            {
                return info.Name; 
            }
        }
        public static string Folder0_PythonInit { get { return "0.Initialize Python"; } }
        public static string Folder1_Param { get { return "1.Parameters"; } }
        public static string Folder2_ConstructFEM { get { return "2.Construct FEModel"; } }
        public static string Folder3_StaticLoading { get { return "3.Static Loading"; } }
        public static string Folder4_StaticSolvers { get { return "4.Static Solvers"; } }
        public static string Folder5_DeconstructFEM { get { return "5.Deconstruct FEModel"; } }
        public static string Folder6_Dynamic { get { return "6.Dynamic Modal Analysis"; } }
        public static string Folder7_Display { get { return "7.Display"; } } 
        public static string Folder8_Util { get { return "8.Utilities"; } } 

    }
}