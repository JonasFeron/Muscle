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
using System.Linq;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Converts Element instances to CoreElements for computational analysis.
    /// </summary>
    public static class ElementsEncoder
    {
        /// <summary>
        /// Converts a collection of Element instances to a CoreElements instance for computational analysis.
        /// </summary>
        /// <param name="elements">Collection of Element instances to convert</param>
        /// <param name="coreNodes">CoreNodes instance that contains the nodes referenced by the elements</param>
        /// <returns>CoreElements instance containing all element data needed for analysis</returns>
        public static CoreElements ToCoreElements(IEnumerable<Element> elements, CoreNodes coreNodes)
        {
            if (elements == null || !elements.Any())
                throw new ArgumentException("Elements collection cannot be null or empty");
            
            if (coreNodes == null)
                throw new ArgumentNullException(nameof(coreNodes), "CoreNodes instance cannot be null");
            
            int count = elements.Count();
            
            // Initialize arrays
            int[] type = new int[count];
            int[,] endNodes = new int[count, 2];
            double[] area = new double[count];
            double[,] youngs = new double[count, 2];
            double[] freeLength = new double[count];
            double[] tension = new double[count];
            
            // Populate arrays from elements
            int i = 0;
            foreach (var element in elements)
            {
                // Element type (-1 for struts, 1 for cables, 0 for both)
                type[i] = element.Type;
                
                // End nodes indices
                if (element.EndNodes.Count >= 2)
                {
                    endNodes[i, 0] = element.EndNodes[0];
                    endNodes[i, 1] = element.EndNodes[1];
                }
                else
                {
                    throw new ArgumentException($"Element at index {i} does not have exactly 2 end nodes");
                }
                
                // Cross-sectional area
                area[i] = element.CS.Area;
                
                // Young's moduli
                youngs[i, 0] = element.Material.Ec; // Young's modulus for compression
                youngs[i, 1] = element.Material.Et; // Young's modulus for tension
                
                // Free length
                freeLength[i] = element.FreeLength;
                
                // Current tension
                tension[i] = element.Tension;
                
                i++;
            }
            
            // Create and return CoreElements instance
            return new CoreElements(
                coreNodes,
                type,
                endNodes,
                area,
                youngs,
                freeLength,
                tension
            );
        }
        
    }
}
