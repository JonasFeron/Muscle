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
        /// Updates a list of Element instances with data from a FEM_Elements instance.
        /// </summary>
        /// <param name="elements">List of Element instances to update</param>
        /// <param name="femElements">FEM_Elements instance containing element data</param>
        /// <param name="nodes">List of Node instances to get coordinates for creating the Lines</param>
        /// <returns>Updated list of Element instances</returns>
        public static List<Element> CopyAndUpdateFrom(List<Element> elements, FEM_Elements femElements, List<Node> nodes)
        {
            if (elements == null)
                throw new ArgumentNullException(nameof(elements), "Elements list cannot be null");

            if (femElements == null)
                throw new ArgumentNullException(nameof(femElements), "FEM_Elements cannot be null");

            if (nodes == null || nodes.Count == 0)
                throw new ArgumentException("Nodes collection cannot be null or empty", nameof(nodes));

            if (elements.Count != femElements.Count)
                throw new ArgumentException("Elements list and FEM_Elements arrays must have the same length");

            // Create a new list to hold the updated elements
            List<Element> updatedElements = new List<Element>();

            // Update each element
            for (int i = 0; i < femElements.Count; i++)
            {
                // Create a copy of the original element
                Element updatedElement = elements[i].Copy();
                
                // Update Line with new nodes coordinates              
                int node_idx0 = updatedElement.EndNodes[i,0];
                int node_idx1  = updatedElement.EndNodes[i,1];
                Point3d p0 = nodes[node_idx0].Point; // new coordinates of End Nodes
                Point3d p1 = nodes[node_idx1].Point; 
                updatedElement.Line = new Line(p0, p1);
                
                // Update free length and tension
                updatedElement.FreeLength = femElements.FreeLength[i];
                updatedElement.Tension = femElements.Tension[i];
                
                // Add the updated element to the list
                updatedElements.Add(updatedElement);
            }
            
            return updatedElements;
        }
    }
}
