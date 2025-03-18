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
