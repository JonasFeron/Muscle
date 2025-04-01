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
using Grasshopper.Kernel.Types;

namespace MuscleApp.Converters
{

    public static class PrestressEncoder
    {

        /// <summary>
        /// Adds up all prestress instances. If more than one prestress is defined by the user on the same element, the values are added up.
        /// </summary>
        /// <param name="prestress">Collection of Prestress instances</param>
        /// <param name="elementCount">Number of elements in the structure</param>
        /// <returns>Array of free length variations with combined values for each element</returns>
        public static double[] AddsUpAllPrestress(IEnumerable<Prestress> prestress, int elementCount)
        {
            // Create a free length variation array with initial values of 0.0 for each element. 
            double[] freeLengthVariation = new double[elementCount];
            
            // Populate the free length variations by adding up values for the same element
            foreach (Prestress p in prestress)
            {
                if (p != null && p.Element != null && p.IsValid)
                {
                    // retrieve element index on which the prestress is applied. 
                    int elementIndex = p.Element.Idx;
                    if (elementIndex >= 0 && elementIndex < freeLengthVariation.Length)
                    {
                        // Add the value to the existing value (in case multiple scenarios affect the same element)
                        freeLengthVariation[elementIndex] += p.FreeLengthVariation;
                    }
                }
            }
            
            return freeLengthVariation;
        }
    }
}
