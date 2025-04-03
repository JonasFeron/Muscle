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
    /// Static class for decoding CoreNodes instances to Node instances.
    /// </summary>
    public static class NodesDecoder
    {

        /// <summary>
        /// Updates a list of Node instances with results from a CoreNodes instance after computations.
        /// </summary>
        /// <param name="originalNodes">List of Node instances to update</param>
        /// <param name="coreNodesResults">CoreNodes instance containing node results</param>
        /// <returns>Updated list of Node instances</returns>
        public static List<Node> CopyAndUpdate(List<Node> originalNodes, CoreNodes coreNodesResults)
        {
            if (originalNodes == null)
                throw new ArgumentNullException(nameof(originalNodes), "Nodes list cannot be null");

            if (coreNodesResults == null)
                throw new ArgumentNullException(nameof(coreNodesResults), "CoreNodes cannot be null");

            if (originalNodes.Count != coreNodesResults.Count)
                throw new ArgumentException("Nodes list and CoreNodes arrays must have the same length");

            // Create a new list to hold the updated nodes
            List<Node> updatedNodes = new List<Node>();

            // Update each node
            for (int i = 0; i < coreNodesResults.Count; i++)
            {
                // Create a copy of the original node
                Node updatedNode = originalNodes[i].Copy();
                                
                // Update point from final coordinates ( initial_coordinates + displacements)
                updatedNode.Coordinates = new Point3d(
                    coreNodesResults.Coordinates[i, 0],
                    coreNodesResults.Coordinates[i, 1],
                    coreNodesResults.Coordinates[i, 2]
                );

                // // Update DOF constraints (true = free, false = fixed)
                // updatedNode.isXFree = femNodes.DOF[i, 0];
                // updatedNode.isYFree = femNodes.DOF[i, 1];
                // updatedNode.isZFree = femNodes.DOF[i, 2];

                // Update loads
                updatedNode.Loads = new Vector3d(
                    coreNodesResults.Loads[i, 0],
                    coreNodesResults.Loads[i, 1],
                    coreNodesResults.Loads[i, 2]
                );

                // Update reactions
                updatedNode.Reactions = new Vector3d(
                    coreNodesResults.Reactions[i, 0],
                    coreNodesResults.Reactions[i, 1],
                    coreNodesResults.Reactions[i, 2]
                );

                // Update residuals
                updatedNode.Residuals = new Vector3d(
                    coreNodesResults.Residuals[i, 0],
                    coreNodesResults.Residuals[i, 1],
                    coreNodesResults.Residuals[i, 2]
                );

                // Add the updated node to the list
                updatedNodes.Add(updatedNode);
            }

            return updatedNodes;
        }
    }
}