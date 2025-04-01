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

using Rhino.Geometry;
using System;
using System.Collections.Generic;
using MuscleApp.ViewModel;
using MuscleCore.FEModel;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Static class for decoding CoreTruss instances to Truss instances.
    /// </summary>
    public static class TrussDecoder
    {
        /// <summary>
        /// Updates a Truss instance with results from a CoreTruss instance.
        /// </summary>
        /// <param name="original">Truss instance to update</param>
        /// <param name="coreTrussResults">CoreTruss instance containing structure results</param>
        /// <returns>Updated Truss instance</returns>
        public static Truss CopyAndUpdate(Truss original, CoreTruss coreTrussResults)
        {
            if (original == null)
                throw new ArgumentNullException(nameof(original), "Truss cannot be null");
                
            if (coreTrussResults == null)
                throw new ArgumentNullException(nameof(coreTrussResults), "CoreTruss cannot be null");
                
            if (coreTrussResults.Nodes == null || coreTrussResults.Elements == null)
                throw new ArgumentException("CoreTruss must have valid Nodes and Elements", nameof(coreTrussResults));
            
            // Create a copy of the original structure state
            Truss updated = original.Copy();

            // retrieve the results from the computations stored in coreTrussResults
            CoreNodes nodesResults = coreTrussResults.Nodes;
            CoreElements elementsResults = coreTrussResults.Elements;
            
            // Copy and Update original nodes with the nodes results 
            updated.Nodes = NodesDecoder.CopyAndUpdate(original.Nodes, nodesResults);
            
            // Copy and Update original elements with the elements results
            updated.Elements = ElementsDecoder.CopyAndUpdate(original.Elements, elementsResults, updated.Nodes);
            
            // Update equilibrium state
            updated.IsInEquilibrium = coreTrussResults.IsInEquilibrium;

            return updated;
        }
    }
}