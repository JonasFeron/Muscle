using Rhino.Geometry;
using System;
using System.Collections.Generic;
using Muscle.ViewModel;
using MuscleCore.FEModel;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Static class for decoding FEM_Nodes instances to Node instances.
    /// </summary>
    public static class NodesDecoder
    {

        /// <summary>
        /// Updates a list of Node instances with data from a FEM_Nodes instance after computations.
        /// </summary>
        /// <param name="originalNodes">List of Node instances to update</param>
        /// <param name="femNodesResults">FEM_Nodes instance containing node results</param>
        /// <returns>Updated list of Node instances</returns>
        public static List<Node> CopyAndUpdateFrom(List<Node> originalNodes, FEM_Nodes femNodesResults)
        {
            if (originalNodes == null)
                throw new ArgumentNullException(nameof(originalNodes), "Nodes list cannot be null");

            if (femNodesResults == null)
                throw new ArgumentNullException(nameof(femNodesResults), "FEM_Nodes cannot be null");

            if (originalNodes.Count != femNodesResults.Count)
                throw new ArgumentException("Nodes list and FEM_Nodes arrays must have the same length");

            // Create a new list to hold the updated nodes
            List<Node> updatedNodes = new List<Node>();

            // Update each node
            for (int i = 0; i < femNodesResults.Count; i++)
            {
                // Create a copy of the original node
                Node updatedNode = originalNodes[i].Copy();
                                
                // Update point from final coordinates ( initial_coordinates + displacements)
                updatedNode.Coordinates = new Point3d(
                    femNodesResults.Coordinates[i, 0],
                    femNodesResults.Coordinates[i, 1],
                    femNodesResults.Coordinates[i, 2]
                );

                // // Update DOF constraints (true = free, false = fixed)
                // updatedNode.isXFree = femNodes.DOF[i, 0];
                // updatedNode.isYFree = femNodes.DOF[i, 1];
                // updatedNode.isZFree = femNodes.DOF[i, 2];

                // Update loads
                updatedNode.Loads = new Vector3d(
                    femNodesResults.Loads[i, 0],
                    femNodesResults.Loads[i, 1],
                    femNodesResults.Loads[i, 2]
                );

                // Update reactions
                updatedNode.Reactions = new Vector3d(
                    femNodesResults.Reactions[i, 0],
                    femNodesResults.Reactions[i, 1],
                    femNodesResults.Reactions[i, 2]
                );

                // Update residuals
                updatedNode.Residuals = new Vector3d(
                    femNodesResults.Residuals[i, 0],
                    femNodesResults.Residuals[i, 1],
                    femNodesResults.Residuals[i, 2]
                );

                // Add the updated node to the list
                updatedNodes.Add(updatedNode);
            }

            return updatedNodes;
        }
    }
}