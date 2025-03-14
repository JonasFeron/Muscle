using System;

namespace MuscleCore.FEModel
{
    /// <summary>
    /// Data container for FEM_Nodes. All computations and logic are handled in the Python equivalent class.
    /// This class serves as a pure data transfer object between C# and Python.
    /// </summary>
    public class FEM_Nodes
    {
        #region Properties
        /// <summary>
        /// [m] - shape (nodes_count, 3) - Initial nodal coordinates
        /// </summary>
        public double[,] InitialCoordinates { get; set; }

        /// <summary>
        /// [m] - shape (nodes_count, 3) - Current nodal coordinates (initial_coordinates + displacements)
        /// </summary>
        public double[,] Coordinates { get; set; }

        /// <summary>
        /// [-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)
        /// </summary>
        public bool[,] DOF { get; set; }

        /// <summary>
        /// Number of nodes
        /// </summary>
        public int Count { get; set; }

        /// <summary>
        /// Number of fixed degrees of freedom
        /// </summary>
        public int FixationsCount { get; set; }

        /// <summary>
        /// [N] - shape (nodes_count, 3) - External loads applied to nodes
        /// </summary>
        public double[,] Loads { get; set; }

        /// <summary>
        /// [m] - shape (nodes_count, 3) - Nodal displacements
        /// </summary>
        public double[,] Displacements { get; set; }

        /// <summary>
        /// [N] - shape (nodes_count, 3) - Support reactions
        /// </summary>
        public double[,] Reactions { get; set; }

        /// <summary>
        /// [N] - shape (nodes_count, 3) - Internal resisting forces at nodes
        /// </summary>
        public double[,] ResistingForces { get; set; }

        /// <summary>
        /// [N] - shape (nodes_count, 3) - Out of balance loads (loads + reactions - resisting_forces)
        /// </summary>
        public double[,] Residual { get; set; }
        #endregion

        #region Constructors
        /// <summary>
        /// Initialize FEM_Nodes data container with minimal required data. All computations will be done in Python.
        /// </summary>
        /// <param name="initialCoordinates">[m] - shape (nodes_count, 3) - Initial nodal coordinates</param>
        /// <param name="dof">[-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)</param>
        /// <param name="loads">[N] - shape (nodes_count, 3) - External loads applied to nodes</param>
        /// <param name="displacements">[m] - shape (nodes_count, 3) - Nodal displacements</param>
        /// <param name="reactions">[N] - shape (nodes_count, 3) - Support reactions</param>
        /// <param name="resistingForces">[N] - shape (nodes_count, 3) - Internal resisting forces at nodes</param>
        public FEM_Nodes(double[,] initialCoordinates, bool[,] dof, double[,] loads = null, 
                        double[,] displacements = null, double[,] reactions = null, double[,] resistingForces = null)
        {
            // Initialize properties
            InitialCoordinates = initialCoordinates ?? throw new ArgumentNullException(nameof(initialCoordinates));
            DOF = dof ?? throw new ArgumentNullException(nameof(dof));
            Count = initialCoordinates.GetLength(0);
            
            // Initialize mutable properties with default values if null
            FixationsCount = 0;
            Coordinates = new double[Count, 3];
            Loads = loads ?? new double[Count, 3];
            Displacements = displacements ?? new double[Count, 3];
            Reactions = reactions ?? new double[Count, 3];
            ResistingForces = resistingForces ?? new double[Count, 3];
            Residual = new double[Count, 3];
        }

        /// <summary>
        /// Initialize FEM_Nodes data container with all properties. Used when decoding from Python where all values are known.
        /// </summary>
        /// <param name="initialCoordinates">[m] - shape (nodes_count, 3) - Initial nodal coordinates</param>
        /// <param name="coordinates">[m] - shape (nodes_count, 3) - Current nodal coordinates</param>
        /// <param name="dof">[-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)</param>
        /// <param name="count">Number of nodes</param>
        /// <param name="fixationsCount">Number of fixed degrees of freedom</param>
        /// <param name="loads">[N] - shape (nodes_count, 3) - External loads applied to nodes</param>
        /// <param name="displacements">[m] - shape (nodes_count, 3) - Nodal displacements</param>
        /// <param name="reactions">[N] - shape (nodes_count, 3) - Support reactions</param>
        /// <param name="resistingForces">[N] - shape (nodes_count, 3) - Internal resisting forces at nodes</param>
        /// <param name="residual">[N] - shape (nodes_count, 3) - Out of balance loads</param>
        public FEM_Nodes(
            double[,] initialCoordinates,
            double[,] coordinates,
            bool[,] dof,
            int count,
            int fixationsCount,
            double[,] loads,
            double[,] displacements,
            double[,] reactions,
            double[,] resistingForces,
            double[,] residual)
        {
            InitialCoordinates = initialCoordinates ?? throw new ArgumentNullException(nameof(initialCoordinates));
            Coordinates = coordinates ?? throw new ArgumentNullException(nameof(coordinates));
            DOF = dof ?? throw new ArgumentNullException(nameof(dof));
            Count = count;
            FixationsCount = fixationsCount;
            Loads = loads ?? throw new ArgumentNullException(nameof(loads));
            Displacements = displacements ?? throw new ArgumentNullException(nameof(displacements));
            Reactions = reactions ?? throw new ArgumentNullException(nameof(reactions));
            ResistingForces = resistingForces ?? throw new ArgumentNullException(nameof(resistingForces));
            Residual = residual ?? throw new ArgumentNullException(nameof(residual));
        }
        #endregion
    }
}