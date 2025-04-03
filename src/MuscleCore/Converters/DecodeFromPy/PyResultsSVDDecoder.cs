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

using MuscleCore.Solvers;
using Python.Runtime;
using static MuscleCore.Converters.DecoderHelper;

namespace MuscleCore.Converters
{
    /// <summary>
    /// Decoder for converting Python SVDresults objects to C# CoreResultsSVD objects.
    /// </summary>
    public class PyResultsSVDDecoder : IPyObjectDecoder
    {
        /// <summary>
        /// Determines if this decoder can decode the given Python object type to the specified target type.
        /// </summary>
        /// <param name="objectType">The Python object type</param>
        /// <param name="targetType">The target C# type</param>
        /// <returns>True if this decoder can decode the object, false otherwise</returns>
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(CoreResultsSVD))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "PyResultsSVD";
                }
                catch
                {
                    return false;
                }
            }
        }

        /// <summary>
        /// Attempts to decode a Python SVDresults object to a C# CoreResultsSVD object.
        /// </summary>
        /// <typeparam name="T">The target type (must be CoreResultsSVD)</typeparam>
        /// <param name="pyObj">The Python object to decode</param>
        /// <param name="value">The decoded value, if successful</param>
        /// <returns>True if decoding was successful, false otherwise</returns>
        public bool TryDecode<T>(PyObject pyObj, out T? value)
        {
            value = default;
            if (typeof(T) != typeof(CoreResultsSVD))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Extract scalar values
                    int r = (int)py.r;
                    int s = (int)py.s;
                    int m = (int)py.m;

                    // Extract matrices and convert to C# arrays
                    // Note: We're getting the transposed matrices directly from Python
                    var ur_T = As2dArray(py.Ur_T);
                    var um_T = As2dArray(py.Um_T);
                    var sr = py.Sr.tolist().As<double[]>();
                    var vr_T = As2dArray(py.Vr_T);
                    var vs_T = As2dArray(py.Vs_T);

                    // Create CoreResultsSVD object with all properties
                    var svdResults = new CoreResultsSVD(
                        r: r,
                        s: s,
                        m: m,
                        ur_T: ur_T,
                        um_T: um_T,
                        sr: sr,
                        vr_T: vr_T,
                        vs_T: vs_T
                    );

                    value = (T)(object)svdResults;
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in TryDecode: {ex.Message}\n{ex.StackTrace}");
                    return false;
                }
            }
        }
    }
}
