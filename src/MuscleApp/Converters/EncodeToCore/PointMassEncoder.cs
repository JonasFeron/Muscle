using MuscleCore.FEModel;
using MuscleApp.ViewModel;
using System;
using System.Collections.Generic;
using System.Linq;
using Rhino.Geometry;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Utility class for encoding PointMass objects to arrays suitable for MuscleCore
    /// </summary>
    public static class PointMassEncoder
    {
        /// <summary>
        /// Adds up all point masses. If more than one mass is defined by the user on the same node, the values are added up.
        /// </summary>
        /// <param name="pointMasses">Collection of PointMass instances</param>
        /// <param name="nodes">List of nodes in the structure</param>
        /// <param name="zeroTolerance">Tolerance for determining if a point is at the same location as a node</param>
        /// <param name="warnings">Optional list to store warnings</param>
        /// <returns>Array of loads with combined values for each node's degrees of freedom</returns>
        public static double[] AddsUpAllPointMasses(IEnumerable<PointMass> pointMasses, List<Node> nodes, double zeroTolerance, List<string>? warnings = null)
        {
            if (nodes == null || !nodes.Any())
                throw new ArgumentException("Nodes list cannot be null or empty", nameof(nodes));
                
            int nodeCount = nodes.Count;
            
            // Create a loads array with initial values of 0.0 for each node's DOF (3 DOFs per node)
            double[] pointMassesArray = new double[nodeCount * 3];
            
            // Populate the loads array by adding up values for the same node
            foreach (PointMass pointMass in pointMasses)
            {
                if (pointMass == null)
                {
                    continue;
                }
                    
                int nodeIdx = -1;
                
                // Check if the point mass is defined by a node index
                if (pointMass.NodeInd >= 0)
                {
                    nodeIdx = pointMass.NodeInd;
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
                // If not defined by node index, try to find a node at the same location as the point mass point
                else
                {
                    if (!Node.EpsilonContains(nodes, pointMass.Point, zeroTolerance, out nodeIdx))
                    {
                        // No node found at the point mass point within tolerance
                        if (warnings != null)
                        {
                            warnings.Add($"A point mass is applied on a point ({pointMass.Point.X:F3}, {pointMass.Point.Y:F3}, {pointMass.Point.Z:F3}) which does not belong to the structure. This point mass is ignored.");
                        }
                        continue;
                    }
                }
                
                // Add the mass components to the existing values
                // (in case multiple masses affect the same node)
                pointMassesArray[3*nodeIdx]     += pointMass.Vector.X; // X component
                pointMassesArray[3*nodeIdx + 1] += pointMass.Vector.Y; // Y component
                pointMassesArray[3*nodeIdx + 2] += pointMass.Vector.Z; // Z component
            }
            
            return pointMassesArray;
        }
        
        /// <summary>
        /// Overload that accepts a Truss object to determine the nodes
        /// </summary>
        /// <param name="pointMasses">Collection of PointMass instances</param>
        /// <param name="truss">The truss structure containing the nodes</param>
        /// <returns>Array of masses with combined values for each node's degrees of freedom</returns>
        public static double[] AddsUpAllPointMasses(IEnumerable<PointMass> pointMasses, Truss truss)
        {
            if (truss == null)
                throw new ArgumentNullException(nameof(truss));
                
            return AddsUpAllPointMasses(pointMasses, truss.Nodes, truss.ZeroGeometricATol, truss.warnings);
        }
    }
}
