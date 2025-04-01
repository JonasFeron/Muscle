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
using Rhino.Geometry;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Utility class for encoding PointLoad objects to arrays suitable for MuscleCore
    /// </summary>
    public static class PointLoadEncoder
    {
        /// <summary>
        /// Adds up all point loads. If more than one load is defined by the user on the same node, the values are added up.
        /// </summary>
        /// <param name="pointLoads">Collection of PointLoad instances</param>
        /// <param name="nodes">List of nodes in the structure</param>
        /// <param name="zeroTolerance">Tolerance for determining if a point is at the same location as a node</param>
        /// <param name="warnings">Optional list to store warnings</param>
        /// <returns>Array of loads with combined values for each node's degrees of freedom</returns>
        public static double[] AddsUpAllPointLoads(IEnumerable<PointLoad> pointLoads, List<Node> nodes, double zeroTolerance, List<string>? warnings = null)
        {
            if (nodes == null || !nodes.Any())
                throw new ArgumentException("Nodes list cannot be null or empty", nameof(nodes));
                
            int nodeCount = nodes.Count;
            
            // Create a loads array with initial values of 0.0 for each node's DOF (3 DOFs per node)
            double[] loadsArray = new double[nodeCount * 3];
            
            // Populate the loads array by adding up values for the same node
            foreach (PointLoad load in pointLoads)
            {
                if (load == null || !load.IsValid)
                {
                    continue;
                }
                    
                int nodeIdx = -1;
                
                // Check if the load is defined by a node index
                if (load.NodeIdx >= 0)
                {
                    nodeIdx = load.NodeIdx;
                    if (nodeIdx >= nodeCount)
                    {
                        // Node index out of range
                        if (warnings != null)
                        {
                            warnings.Add($"A point load is applied on node index {nodeIdx} which does not exist in the structure. This point load is ignored.");
                        }
                        continue;
                    }
                }
                // If not defined by node index, try to find a node at the same location as the load point
                else
                {
                    if (!Node.EpsilonContains(nodes, load.Point, zeroTolerance, out nodeIdx))
                    {
                        // No node found at the load point within tolerance
                        if (warnings != null)
                        {
                            warnings.Add($"A point load is applied on a point ({load.Point.X:F3}, {load.Point.Y:F3}, {load.Point.Z:F3}) which does not belong to the structure. This point load is ignored.");
                        }
                        continue;
                    }
                }
                
                // Add the load components to the existing values
                // (in case multiple loads affect the same node)
                loadsArray[3*nodeIdx]     += load.Vector.X; // X component
                loadsArray[3*nodeIdx + 1] += load.Vector.Y; // Y component
                loadsArray[3*nodeIdx + 2] += load.Vector.Z; // Z component
            }
            
            return loadsArray;
        }
        
        /// <summary>
        /// Overload that accepts a Truss object to determine the nodes
        /// </summary>
        /// <param name="pointLoads">Collection of PointLoad instances</param>
        /// <param name="truss">The truss structure containing the nodes</param>
        /// <returns>Array of loads with combined values for each node's degrees of freedom</returns>
        public static double[] AddsUpAllPointLoads(IEnumerable<PointLoad> pointLoads, Truss truss)
        {
            if (truss == null)
                throw new ArgumentNullException(nameof(truss));
                
            return AddsUpAllPointLoads(pointLoads, truss.Nodes, truss.ZeroGeometricATol, truss.warnings);
        }
    }
}
