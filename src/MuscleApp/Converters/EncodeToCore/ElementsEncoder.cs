using MuscleCore.FEModel;
using MuscleApp.ViewModel;
using System;
using System.Collections.Generic;
using System.Linq;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Converts Element instances to FEM_Elements for computational analysis.
    /// </summary>
    public static class ElementsEncoder
    {
        /// <summary>
        /// Converts a collection of Element instances to a FEM_Elements instance for computational analysis.
        /// </summary>
        /// <param name="elements">Collection of Element instances to convert</param>
        /// <param name="femNodes">FEM_Nodes instance that contains the nodes referenced by the elements</param>
        /// <returns>FEM_Elements instance containing all element data needed for analysis</returns>
        public static FEM_Elements ToFEM_Elements(IEnumerable<Element> elements, FEM_Nodes femNodes)
        {
            if (elements == null || !elements.Any())
                throw new ArgumentException("Elements collection cannot be null or empty");
            
            if (femNodes == null)
                throw new ArgumentNullException(nameof(femNodes), "FEM_Nodes instance cannot be null");
            
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
            
            // Create and return FEM_Elements instance
            return new FEM_Elements(
                femNodes,
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
