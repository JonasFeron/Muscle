using System;
using System.Collections.Generic;
using System.Linq;
using MuscleApp.ViewModel;
using MuscleCore.FEModel;
using Rhino.Geometry;

namespace MuscleApp.Solvers
{
    /// <summary>
    /// Provides methods to apply self-stress modes to a structure.
    /// </summary>
    public static class SelfStressScenario
    {
        /// <summary>
        /// Creates a list of prestress objects based on a branch of tension values and applies them to a structure.
        /// </summary>
        /// <param name="structure">The structure to apply the self-stress to</param>
        /// <param name="tensions">A branch of tension values, one for each element in the structure</param>
        /// <returns>A list of prestress objects</returns>
        public static List<Prestress> ComputeFreeLengthVariation(Truss structure, IList<double> tensions)
        {
            // Check if the branch has the same length as the number of elements
            if (tensions.Count != structure.Elements.Count)
            {
                structure.warnings.Add($"The number of axial forces ({tensions.Count}) does not match the number of elements ({structure.Elements.Count})");
                return new List<Prestress>();
            }

            // Create a prestress object for each element based on the tension value
            List<Prestress> prestressList = new List<Prestress>();
            for (int i = 0; i < structure.Elements.Count; i++)
            {
                Element element = structure.Elements[i];
                double tension = tensions[i];
                
                // Create a prestress object using the FromTension method
                Prestress prestress = Prestress.FromTension(element, tension);
                prestressList.Add(prestress);
            }

            // Verify equilibrium by checking that the sum of equivalent point loads is zero for each degree of freedom
            CheckSelfEquilibrium(structure, prestressList);

            return prestressList;
        }

        /// <summary>
        /// Verifies that the sum of equivalent point loads is zero for each degree of freedom,
        /// except for degrees of freedom that are fixed by supports.
        /// </summary>
        /// <param name="structure">The structure to verify</param>
        /// <param name="prestressList">The list of prestress objects</param>
        private static void CheckSelfEquilibrium(Truss structure, List<Prestress> prestressList)
        {
            // Dictionary to store the sum of resisting forces at each node
            Dictionary<int, Vector3d> totalResistingForces = new Dictionary<int, Vector3d>();
            
            // Initialize the dictionary with zero vectors for each node
            foreach (Node node in structure.Nodes)
            {
                totalResistingForces[node.Idx] = Vector3d.Zero;
            }
            
            // Sum up all the equivalent point loads for each node
            foreach (Prestress prestress in prestressList)
            {
                int node0 = prestress.Element.EndNodes[0];
                int node1 = prestress.Element.EndNodes[1];
                
                // Get the equivalent point loads
                PointLoad load0 = prestress.EquivalentPointLoad0;
                PointLoad load1 = prestress.EquivalentPointLoad1;
                
                // Add the loads to the sum for each node
                totalResistingForces[node0] += load0.Vector;
                totalResistingForces[node1] += load1.Vector;
            }
            
            // Check if the sum of resisting forces is zero for each node, except for fixed degrees of freedom
            foreach (Node node in structure.Nodes)
            {
                Vector3d residual = totalResistingForces[node.Idx];
                
                // Check each component (X, Y, Z) of the load sum
                if (node.isXFree && Math.Abs(residual.X) > 1e-6)
                {
                    structure.warnings.Add($"Node {node.Idx}: X-component of resisting force sum is not zero ({residual.X:F6})");
                }
                
                if (node.isYFree && Math.Abs(residual.Y) > 1e-6)
                {
                    structure.warnings.Add($"Node {node.Idx}: Y-component of resisting force sum is not zero ({residual.Y:F6})");
                }
                
                if (node.isZFree && Math.Abs(residual.Z) > 1e-6)
                {
                    structure.warnings.Add($"Node {node.Idx}: Z-component of resisting force sum is not zero ({residual.Z:F6})");
                }
            }
        }
    }
}