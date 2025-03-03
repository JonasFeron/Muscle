using System;

namespace MuscleCore.FEModel
{
    public class FEM_Nodes
    {
        #region Properties
        /// <summary>
        /// [m] - shape (nodes_count, 3) - Initial nodal coordinates
        /// </summary>
        public double[,] InitialCoordinates { get; }

        /// <summary>
        /// [m] - shape (nodes_count, 3) - Current nodal coordinates
        /// </summary>
        public double[,] Coordinates { get; set; }

        /// <summary>
        /// [-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)
        /// </summary>
        public bool[,] DOF { get; }

        /// <summary>
        /// Number of nodes
        /// </summary>
        public int Count { get; }

        /// <summary>
        /// Number of fixed degrees of freedom
        /// </summary>
        public int FixationsCount { get; }

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
        /// [N] - shape (nodes_count, 3) - Out of balance loads
        /// </summary>
        public double[,] Residual { get; set; }
        #endregion

        #region Constructor
        /// <summary>
        /// Initialize FEM_Nodes with node properties. All computations will be done in Python.
        /// </summary>
        /// <param name="initialCoordinates">[m] - shape (nodes_count, 3) - Initial nodal coordinates</param>
        /// <param name="dof">[-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)</param>
        /// <param name="loads">[N] - shape (nodes_count, 3) - External loads applied to nodes</param>
        /// <param name="displacements">[m] - shape (nodes_count, 3) - Nodal displacements</param>
        /// <param name="reactions">[N] - shape (nodes_count, 3) - Support reactions</param>
        /// <param name="resistingForces">[N] - shape (nodes_count, 3) - Internal resisting forces at nodes</param>
        /// <exception cref="ArgumentNullException">Thrown when required parameters are null</exception>
        public FEM_Nodes(double[,] initialCoordinates, bool[,] dof, double[,] loads = null, 
                        double[,] displacements = null, double[,] reactions = null, double[,] resistingForces = null)
        {
            // Validate required parameters
            InitialCoordinates = initialCoordinates ?? throw new ArgumentNullException(nameof(initialCoordinates));
            DOF = dof ?? throw new ArgumentNullException(nameof(dof));

            // Set count and validate array dimensions
            Count = InitialCoordinates.GetLength(0);
            if (InitialCoordinates.GetLength(1) != 3)
                throw new ArgumentException("Initial coordinates must have 3 columns", nameof(initialCoordinates));
            if (DOF.GetLength(0) != Count || DOF.GetLength(1) != 3)
                throw new ArgumentException($"DOF must have shape ({Count}, 3)", nameof(dof));

            // Calculate fixations count
            FixationsCount = 0;
            for (int i = 0; i < DOF.GetLength(0); i++)
                for (int j = 0; j < DOF.GetLength(1); j++)
                    if (!DOF[i, j]) FixationsCount++;

            // Initialize mutable properties
            Coordinates = new double[Count, 3];
            Loads = loads ?? new double[Count, 3];
            Displacements = displacements ?? new double[Count, 3];
            Reactions = reactions ?? new double[Count, 3];
            ResistingForces = resistingForces ?? new double[Count, 3];
            Residual = new double[Count, 3];

            // Validate optional array dimensions if provided
            ValidateArrayDimensions(loads, nameof(loads));
            ValidateArrayDimensions(displacements, nameof(displacements));
            ValidateArrayDimensions(reactions, nameof(reactions));
            ValidateArrayDimensions(resistingForces, nameof(resistingForces));
        }
        #endregion

        #region Private Methods
        private void ValidateArrayDimensions(double[,] array, string paramName)
        {
            if (array != null && (array.GetLength(0) != Count || array.GetLength(1) != 3))
                throw new ArgumentException($"{paramName} must have shape ({Count}, 3)", paramName);
        }
        #endregion
    }
}