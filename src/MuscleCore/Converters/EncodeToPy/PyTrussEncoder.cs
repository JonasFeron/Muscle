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

namespace MuscleCore.Converters
{
    public class PyTrussEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(CoreTruss);
        }

        public PyObject? TryEncode(object? obj)
        {
            if (obj == null || !CanEncode(obj.GetType()))
                return null;

            var structure = (CoreTruss)obj;
            using (Py.GIL())
            {
                try
                {
                    dynamic musclepy = Py.Import("MusclePy");
                    dynamic pyElements = structure.Elements.ToPython();
                    dynamic pyNodes = pyElements.nodes;

                    return musclepy.PyTruss(
                        nodes: pyNodes,
                        elements: pyElements
                    );
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in TryEncode: {ex.Message}\n{ex.StackTrace}");
                    return null;
                }
            }
        }
    }
}
