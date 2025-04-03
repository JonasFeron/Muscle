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

using System;

namespace MuscleCore.FEModel
{
    /// <summary>
    /// Pure data container for CoreTruss, combining nodes and elements.
    /// All computations are handled in the Python equivalent (fem_structure.py).
    /// </summary>
    public class CoreTruss
    {
        /// <summary>
        /// Get or set the CoreNodes instance
        /// </summary>
        public CoreNodes Nodes { get; set; }

        /// <summary>
        /// Get or set the CoreElements instance
        /// </summary>
        public CoreElements Elements { get; set; }

        /// <summary>
        /// Get or set whether the structure is in equilibrium.
        /// If loads magnitude is 1000N, the structure is considered in equilibrium 
        /// if the residual magnitude is inferior to 1e-4 * 1000N = 0.1 N
        /// </summary>
        public bool IsInEquilibrium { get; set; }

        /// <summary>
        /// Minimal constructor that validates node references
        /// </summary>
        public CoreTruss(CoreNodes nodes, CoreElements elements)
        {
            Nodes = nodes ?? throw new ArgumentNullException(nameof(nodes));
            Elements = elements ?? throw new ArgumentNullException(nameof(elements));

            if (Elements.Nodes != nodes)
            {
                throw new ArgumentException("Elements must reference the same nodes instance", nameof(elements));
            }
        }

        /// <summary>
        /// Full constructor for setting all properties, used when decoding from Python
        /// </summary>
        public CoreTruss(
            CoreNodes nodes,
            CoreElements elements,
            bool isInEquilibrium)
            : this(nodes, elements)  // Call minimal constructor for validation
        {
            IsInEquilibrium = isInEquilibrium;
        }
    }
}
