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

using MuscleCore.FEModel;
using MuscleApp.ViewModel;
using System;
using System.Collections.Generic;
using static MuscleApp.Converters.NodesEncoder;
using static MuscleApp.Converters.ElementsEncoder;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Converts Truss instances to CoreTruss for computational analysis.
    /// </summary>
    public static class TrussEncoder
    {
        /// <summary>
        /// Converts a Truss instance to a CoreTruss instance for computational analysis.
        /// </summary>
        /// <param name="structure">Truss instance to convert</param>
        /// <returns>CoreTruss instance containing all data needed for analysis</returns>
        public static CoreTruss ToCore(Truss structure)
        {
            if (structure == null)
                throw new ArgumentNullException(nameof(structure), "Truss cannot be null");
            
            if (structure.Nodes.Count == 0)
                throw new ArgumentException("Truss must have at least one node", nameof(structure));
            
            if (structure.Elements.Count == 0)
                throw new ArgumentException("Truss must have at least one element", nameof(structure));
            
            // First convert nodes
            List<Node> nodes = structure.Nodes;
            CoreNodes coreNodes = ToCoreNodes(nodes);
            
            // Then convert elements, using the converted nodes
            List<Element> elements = structure.Elements;
            CoreElements coreElements = ToCoreElements(elements, coreNodes);
            
            // Create the CoreTruss for computational analysis
            return new CoreTruss(coreNodes, coreElements);
        }
    }
}
