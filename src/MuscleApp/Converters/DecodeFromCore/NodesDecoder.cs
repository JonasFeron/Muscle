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
        /// Updates a list of Node instances with data from a FEM_Nodes instance.
        /// </summary>
        /// <param name="nodes">List of Node instances to update</param>
        /// <param name="femNodes">FEM_Nodes instance containing node data</param>
        /// <returns>Updated list of Node instances</returns>
        public static List<Node> CopyAndUpdateFrom(List<Node> nodes, FEM_Nodes femNodes)
        {
            if (nodes == null)
                throw new ArgumentNullException(nameof(nodes), "Nodes list cannot be null");

            if (femNodes == null)
                throw new ArgumentNullException(nameof(femNodes), "FEM_Nodes cannot be null");

            if (nodes.Count != femNodes.Count)
                throw new ArgumentException("Nodes list and FEM_Nodes arrays must have the same length");

            // Create a new list to hold the updated nodes
            List<Node> updatedNodes = new List<Node>();

            // Update each node
            for (int i = 0; i < femNodes.Count; i++)
            {
                // Create a copy of the original node
                Node updatedNode = nodes[i].Copy();
                                
                // Update point from final coordinates
                updatedNode.Point = new Point3d(
                    femNodes.Coordinates[i, 0],
                    femNodes.Coordinates[i, 1],
                    femNodes.Coordinates[i, 2]
                );

                // // Update DOF constraints (true = free, false = fixed)
                // updatedNode.isXFree = femNodes.DOF[i, 0];
                // updatedNode.isYFree = femNodes.DOF[i, 1];
                // updatedNode.isZFree = femNodes.DOF[i, 2];

                // Update loads
                updatedNode.Loads = new Vector3d(
                    femNodes.Loads[i, 0],
                    femNodes.Loads[i, 1],
                    femNodes.Loads[i, 2]
                );

                // Update reactions
                updatedNode.Reactions = new Vector3d(
                    femNodes.Reactions[i, 0],
                    femNodes.Reactions[i, 1],
                    femNodes.Reactions[i, 2]
                );

                // Update residuals
                updatedNode.Residuals = new Vector3d(
                    femNodes.Residuals[i, 0],
                    femNodes.Residuals[i, 1],
                    femNodes.Residuals[i, 2]
                );

                // Add the updated node to the list
                updatedNodes.Add(updatedNode);
            }

            return updatedNodes;
        }
    }
}