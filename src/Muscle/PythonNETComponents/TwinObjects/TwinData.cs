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

//this file was imported from https://github.com/JonasFeron/PythonConnectedGrasshopperTemplate and is used WITHOUT modifications.
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
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

namespace Muscle.PythonNETComponents.TwinObjects
{
    /// <summary>
    /// A Twin data object is used to transfer data between the main Grasshopper/C# thread and the (parallel) python thread.\n
    /// To share a complex object between the C# and Python codes, write the same class in C# and in Python, with identical properties.\n\n
    /// 
    /// For instance, this TwinData class is initialized in C# with a list of double values, a number of rows and a number of columns.\n
    /// The TwinData will be automatically converted into a Python object with the same properties.\n
    /// Then, the Python Script will process the data and return a TwinResult object.\n
    /// The python TwinResult object will be automatically converted into a C# object with the same properties.\n
    /// </summary>
    public class TwinData
    {
        #region Properties

        /// <summary>
        /// Gets the type name of the Twin data.
        /// </summary>
        public string TypeName { get { return "TwinData"; } }

        /// <summary>
        /// Gets or sets the list of double values to be converted into a numpy array with a specific shape (rowNumber, colNumber).
        /// </summary>
        public List<double> AList { get; set; }

        /// <summary>
        /// Gets or sets the number of rows.
        /// </summary>
        public int rowNumber { get; set; }

        /// <summary>
        /// Gets or sets the number of columns.
        /// </summary>
        public int colNumber { get; set; }

        #endregion Properties

        #region Constructors

        /// <summary>
        /// Initializes all properties to their default values.
        /// </summary>
        private void Init()
        {
            AList = new List<double>();
            rowNumber = 0;
            colNumber = 0;
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="TwinData"/> class.
        /// </summary>
        public TwinData()
        {
            Init();
        }

        /// <summary>
        /// Initializes a new instance of the <see cref="TwinData"/> class with specified values.
        /// </summary>
        /// <param name="aList">The list of GH_Number values.</param>
        /// <param name="row">The number of rows.</param>
        /// <param name="col">The number of columns.</param>
        public TwinData(List<GH_Number> aList, int row, int col)
        {
            Init();
            AList = aList.Select(GHNum => GHNum.Value).ToList(); // transform a List of GH_Number into a List of double. 
            rowNumber = row;
            colNumber = col;
        }

        #endregion Constructors

        #region Methods

        #endregion Methods
    }
}