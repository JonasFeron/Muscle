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

using MuscleCore.FEModel;
using Python.Runtime;
using static MuscleCore.Converters.DecoderHelper;

namespace MuscleCore.Converters
{
    public class PyNodesDecoder : IPyObjectDecoder
    {
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(CoreNodes))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "PyNodes" || objectType.Name == "PyNodesDR";
                }
                catch
                {
                    return false;
                }
            }
        }

        public bool TryDecode<T>(PyObject pyObj, out T? value)
        {
            value = default;
            if (typeof(T) != typeof(CoreNodes))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Convert all arrays using the helper
                    var initialCoords = As2dArray(py.initial_coordinates);
                    var coordinates = As2dArray(py.coordinates);
                    var dofs = AsBool2dArray(py.dof);
                    var loads = As2dArray(py.loads);
                    var displacements = As2dArray(py.displacements);
                    var reactions = As2dArray(py.reactions);
                    var resistingForces = As2dArray(py.resisting_forces);
                    var residuals = As2dArray(py.residuals);

                    // Create nodes object with all properties
                    var nodes = new CoreNodes(
                        initialCoordinates: initialCoords,
                        coordinates: coordinates,
                        dof: dofs,
                        count: (int)py.count,
                        loads: loads,
                        displacements: displacements,
                        reactions: reactions,
                        resistingForces: resistingForces,
                        residuals: residuals
                    );

                    value = (T)(object)nodes;
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
