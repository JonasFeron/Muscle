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

using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscle.PythonConnectedComponents.TwinObjects
{
    /// <summary>
    /// A Twin result object is used to transfer result between the (parallel) python thread and the main Grasshopper/C# thread.\n
    /// To share a complex object between the C# and Python codes, write the same class in C# and in Python, with identical properties.\n\n
    /// 
    /// For instance, this TwinResult object is created in Python after processing/reshaping the TwinData\n
    /// The python TwinResult object will be automatically converted into a C# object with the same properties.\n
    /// </summary>
    public class TwinResult
    {
        #region Properties

        public string TypeName { get { return "TwinResult"; } }


        public List<List<double>> Matrix { get; set; } //A matrix 


        #endregion Properties

        #region Constructors


        /// <summary>
        /// Initialize all Properties
        /// </summary>
        private void Init()
        {
            Matrix = new List<List<double>>();
        }


        /// <summary>
        /// Default constructor
        /// </summary>
        public TwinResult()
        {
            Init();
        }


        /// <summary>
        /// Converts a list of lists of doubles to a Grasshopper structure of GH_Numbers.
        /// </summary>
        /// <param name="datalistlist">The list of lists of doubles to convert.</param>
        /// <returns>A GH_Structure containing the converted GH_Numbers.</returns>
        public static GH_Structure<GH_Number> ListListToGH_Struct(List<List<double>> datalistlist)
        {
            GH_Path path;
            int i = 0;
            GH_Structure<GH_Number> res = new GH_Structure<GH_Number>();
            foreach (List<double> datalist in datalistlist)
            {
                path = new GH_Path(i);
                res.AppendRange(datalist.Select(data => new GH_Number(data)), path);
                i++;
            }
            return res;
        }

        #endregion Methods

    }
}
