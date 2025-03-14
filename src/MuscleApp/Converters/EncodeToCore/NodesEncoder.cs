using MuscleCore.FEModel;
using Muscle.ViewModel;

namespace MuscleApp.Converters
{
    public static class NodesEncoder
    {
        /// <summary>
        /// Converts a collection of Node instances into an FEM_Nodes instance.
        /// This function initializes the FEM_Nodes data structure with coordinates, degrees of freedom,
        /// loads, reactions, displacements, and resisting forces derived from the input nodes.
        /// </summary>
        /// <param name="nodes">Collection of Node instances to convert</param>
        /// <returns>FEM_Nodes instance containing all node data needed for analysis</returns>
        public static FEM_Nodes ToFEM_Nodes(IEnumerable<Node> nodes)
        {
            if (nodes == null || !nodes.Any())
                throw new ArgumentException("Nodes collection cannot be null or empty");
            
            int count = nodes.Count();
            
            // Initialize arrays
            double[,] initialCoordinates = new double[count, 3];
            bool[,] dof = new bool[count, 3];
            double[,] loads = new double[count, 3];
            double[,] reactions = new double[count, 3];
            double[,] displacements = new double[count, 3];
            double[,] resistingForces = new double[count, 3];
            
            // Populate arrays from nodes
            int i = 0;
            foreach (Node node in nodes)
            {
                // Convert coordinates: Current coordinates are considered as new initial coordinates
                initialCoordinates[i, 0] = node.Coordinates.X;
                initialCoordinates[i, 1] = node.Coordinates.Y;
                initialCoordinates[i, 2] = node.Coordinates.Z;

                // Reset displacements. 
                displacements[i, 0] = 0;
                displacements[i, 1] = 0;
                displacements[i, 2] = 0;
                
                // Convert DOF (true = free, false = fixed)
                dof[i, 0] = node.isXFree;
                dof[i, 1] = node.isYFree;
                dof[i, 2] = node.isZFree;
                
                // Convert loads
                loads[i, 0] = node.Loads.X;
                loads[i, 1] = node.Loads.Y;
                loads[i, 2] = node.Loads.Z;
                
                // Convert reactions
                reactions[i, 0] = node.Reactions.X;
                reactions[i, 1] = node.Reactions.Y;
                reactions[i, 2] = node.Reactions.Z;
                
                // Calculate resisting forces from loads, reactions, and residuals data contained in the Node instance
                resistingForces[i, 0] = node.Loads.X + node.Reactions.X - node.Residuals.X;
                resistingForces[i, 1] = node.Loads.Y + node.Reactions.Y - node.Residuals.Y;
                resistingForces[i, 2] = node.Loads.Z + node.Reactions.Z - node.Residuals.Z;
                
                i++;
            }
            
            return new FEM_Nodes(
                initialCoordinates, 
                dof, 
                loads, 
                displacements, 
                reactions, 
                resistingForces
            );
        }
    }
}