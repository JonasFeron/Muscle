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
    /// Static class for decoding CoreElements instances to Element instances.
    /// </summary>
    public static class ElementsDecoder
    {
        /// <summary>
        /// Updates a list of Element instances with results from a CoreElements instance after computations.
        /// </summary>
        /// <param name="originalElements">List of Element instances to update</param>
        /// <param name="coreElementsResults">CoreElements instance containing element results</param>
        /// <param name="updatedNodes">List of Node instances to get coordinates for creating the Lines</param>
        /// <returns>Updated list of Element instances</returns>
        public static List<Element> CopyAndUpdate(List<Element> originalElements, CoreElements coreElementsResults, List<Node> updatedNodes)
        {
            if (originalElements == null)
                throw new ArgumentNullException(nameof(originalElements), "Elements list cannot be null");

            if (coreElementsResults == null)
                throw new ArgumentNullException(nameof(coreElementsResults), "CoreElements cannot be null");

            if (updatedNodes == null || updatedNodes.Count == 0)
                throw new ArgumentException("Nodes collection cannot be null or empty", nameof(updatedNodes));

            if (originalElements.Count != coreElementsResults.Count)
                throw new ArgumentException("Elements list and CoreElements arrays must have the same length");

            // Create a new list to hold the updated elements
            List<Element> updatedElements = new List<Element>();

            // Update each element
            for (int i = 0; i < coreElementsResults.Count; i++)
            {
                // Create a copy of the original element
                Element updatedElement = originalElements[i].Copy();
                
                // Update Line with new nodes coordinates              
                int node_idx0 = updatedElement.EndNodes[0];
                int node_idx1  = updatedElement.EndNodes[1];
                Point3d p0 = updatedNodes[node_idx0].Coordinates; // new coordinates of End Nodes
                Point3d p1 = updatedNodes[node_idx1].Coordinates; 
                updatedElement.Line = new Line(p0, p1);
                
                // Update free length and tension
                if (coreElementsResults.FreeLength != null)
                {
                    updatedElement.FreeLength = coreElementsResults.FreeLength[i];
                }
                
                if (coreElementsResults.Tension != null)
                {
                    updatedElement.Tension = coreElementsResults.Tension[i];
                }
                
                // Add the updated element to the list
                updatedElements.Add(updatedElement);
            }
            
            return updatedElements;
        }
    }
}
