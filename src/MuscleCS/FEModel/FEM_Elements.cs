using System;

namespace MuscleCore.FEModel
{
    /// <summary>
    /// Data container for FEM_Elements. All computations and logic are handled in the Python equivalent class.
    /// This class serves as a pure data transfer object between C# and Python.
    /// </summary>
    public class FEM_Elements
    {
        #region Properties
        /// <summary>
        /// FEM_Nodes instance containing nodes data
        /// </summary>
        public FEM_Nodes Nodes { get; set; }

        /// <summary>
        /// [-] - shape (elements_count,) - Type of elements (-1 for struts, 1 for cables)
        /// </summary>
        public int[] Type { get; set; }

        /// <summary>
        /// [-] - shape (elements_count, 2) - Indices of end nodes
        /// </summary>
        public int[,] EndNodes { get; set; }


        /// <summary>
        /// Number of elements
        /// </summary>
        public int Count { get; set; }

        /// <summary>
        /// [MPa] - shape (elements_count, 2) - Young's moduli in compression and tension
        /// </summary>
        public double[,] Youngs { get; set; }

        /// <summary>
        /// [mm²] - shape (elements_count,) - Cross-sectional area of the elements
        /// </summary>
        public double[] Area { get; set; }

        /// <summary>
        /// [MPa] - shape (elements_count,) - Current Young's modulus depending on tension state
        /// </summary>
        public double[] Young { get; set; }

        /// <summary>
        /// [m] - shape (elements_count,) - Current length based on current node coordinates
        /// </summary>
        public double[] CurrentLength { get; set; }

        /// <summary>
        /// [m] - shape (elements_count,) - Free length of the elements
        /// </summary>
        public double[] FreeLength { get; set; }

        /// <summary>
        /// [N] - shape (elements_count,) - Axial force (positive in tension)
        /// </summary>
        public double[] Tension { get; set; }

        /// <summary>
        /// [m/N] - shape (elements_count,) - L/(EA), large value (1e6) if EA ≈ 0
        /// </summary>
        public double[] Flexibility { get; set; }

        /// <summary>
        /// [-] - shape (elements_count, 3) - Unit vectors (x,y,z)
        /// </summary>
        public double[,] DirectionCosines { get; set; }
        #endregion

        #region Constructors
        /// <summary>
        /// Initialize FEM_Elements with minimal required data. All computations will be done in Python.
        /// </summary>
        /// <param name="nodes">FEM_Nodes instance</param>
        /// <param name="type">Element types, shape (elements_count,)</param>
        /// <param name="endNodes">Node indices, shape (elements_count, 2)</param>
        /// <param name="areas">Cross-sections, shape (elements_count, 2) : [A_if_compression, A_if_tension]</param>
        /// <param name="youngs">Young's moduli, shape (elements_count, 2) : [E_if_compression, E_if_tension]</param>
        /// <param name="freeLength">Free length of the elements, shape (elements_count,)</param>
        /// <param name="tension">Axial forces, shape (elements_count,)</param>
        public FEM_Elements(FEM_Nodes nodes, int[] type, int[,] endNodes, double[,] area, 
                          double[,] youngs, double[] freeLength = null, double[] tension = null)
        {
            // Initialize required properties
            Nodes = nodes ?? throw new ArgumentNullException(nameof(nodes));
            Type = type ?? throw new ArgumentNullException(nameof(type));
            EndNodes = endNodes ?? throw new ArgumentNullException(nameof(endNodes));
            Youngs = youngs ?? throw new ArgumentNullException(nameof(youngs));
            Area = area ?? throw new ArgumentNullException(nameof(area));

            // Set count from end nodes
            Count = EndNodes.GetLength(0);

            // Initialize mutable properties with empty arrays

            Young = new double[Count];
            CurrentLength = new double[Count];
            FreeLength = freeLength ?? new double[Count];
            Tension = tension ?? new double[Count];
            Flexibility = new double[Count];
            DirectionCosines = new double[Count, 3];
        }

        /// <summary>
        /// Initialize FEM_Elements with all properties. Used when decoding from Python where all values are known.
        /// </summary>
        public FEM_Elements(
            FEM_Nodes nodes,
            int[] type,
            int[,] endNodes,
            int count,
            double[,] youngs,
            double[] area,
            double[] young,
            double[] currentLength,
            double[] freeLength,
            double[] tension,
            double[] flexibility,
            double[,] directionCosines)
        {
            Nodes = nodes ?? throw new ArgumentNullException(nameof(nodes));
            Type = type ?? throw new ArgumentNullException(nameof(type));
            EndNodes = endNodes ?? throw new ArgumentNullException(nameof(endNodes));
            Count = count;
            Youngs = youngs ?? throw new ArgumentNullException(nameof(youngs));
            Area = area ?? throw new ArgumentNullException(nameof(area));
            Young = young ?? throw new ArgumentNullException(nameof(young));
            CurrentLength = currentLength ?? throw new ArgumentNullException(nameof(currentLength));
            FreeLength = currentFreeLength ?? throw new ArgumentNullException(nameof(currentFreeLength));
            Tension = tension ?? throw new ArgumentNullException(nameof(tension));
            Flexibility = flexibility ?? throw new ArgumentNullException(nameof(flexibility));
            DirectionCosines = directionCosines ?? throw new ArgumentNullException(nameof(directionCosines));
        }
        #endregion
    }
}