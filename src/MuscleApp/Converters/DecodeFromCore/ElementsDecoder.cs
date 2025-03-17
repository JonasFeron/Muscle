using Rhino.Geometry;
using System;
using System.Collections.Generic;
using MuscleApp.ViewModel;
using MuscleCore.FEModel;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Static class for decoding FEM_Elements instances to Element instances.
    /// </summary>
    public static class ElementsDecoder
    {
        /// <summary>
        /// Updates a list of Element instances with results from a FEM_Elements instance after computations.
        /// </summary>
        /// <param name="originalElements">List of Element instances to update</param>
        /// <param name="femElementsResults">FEM_Elements instance containing element results</param>
        /// <param name="updatedNodes">List of Node instances to get coordinates for creating the Lines</param>
        /// <returns>Updated list of Element instances</returns>
        public static List<Element> CopyAndUpdate(List<Element> originalElements, FEM_Elements femElementsResults, List<Node> updatedNodes)
        {
            if (originalElements == null)
                throw new ArgumentNullException(nameof(originalElements), "Elements list cannot be null");

            if (femElementsResults == null)
                throw new ArgumentNullException(nameof(femElementsResults), "FEM_Elements cannot be null");

            if (updatedNodes == null || updatedNodes.Count == 0)
                throw new ArgumentException("Nodes collection cannot be null or empty", nameof(updatedNodes));

            if (originalElements.Count != femElementsResults.Count)
                throw new ArgumentException("Elements list and FEM_Elements arrays must have the same length");

            // Create a new list to hold the updated elements
            List<Element> updatedElements = new List<Element>();

            // Update each element
            for (int i = 0; i < femElementsResults.Count; i++)
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
                updatedElement.FreeLength = femElementsResults.FreeLength[i];
                updatedElement.Tension = femElementsResults.Tension[i];
                
                // Add the updated element to the list
                updatedElements.Add(updatedElement);
            }
            
            return updatedElements;
        }
    }
}
