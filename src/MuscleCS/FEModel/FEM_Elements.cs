using System.Numerics;

namespace MuscleCore.FEModel
{
    public class FEM_Elements
    {
        #region Properties
        /// <summary>
        /// FEM_Nodes instance containing nodes data
        /// </summary>
        public FEM_Nodes Nodes { get; }

        /// <summary>
        /// [-] - shape (elements_count,) - Type of elements (-1 for struts, 1 for cables)
        /// </summary>
        public int[] Type { get; }

        /// <summary>
        /// [-] - shape (elements_count, 2) - Indices of end nodes
        /// </summary>
        public int[,] EndNodes { get; }

        /// <summary>
        /// [m] - shape (elements_count,) - Free length in unprestressed state
        /// </summary>
        public double[] InitialFreeLength { get; set; }

        /// <summary>
        /// Number of elements
        /// </summary>
        public int Count { get; }

        /// <summary>
        /// [mm²] - shape (elements_count, 2) - Areas in compression and tension
        /// </summary>
        public double[,] Areas { get; }

        /// <summary>
        /// [MPa] - shape (elements_count, 2) - Young's moduli in compression and tension
        /// </summary>
        public double[,] Youngs { get; }

        /// <summary>
        /// [mm²] - shape (elements_count,) - Current area depending on tension state
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
        /// [m] - shape (elements_count,) - Current free length (initial + delta)
        /// </summary>
        public double[] CurrentFreeLength { get; set; }

        /// <summary>
        /// [-] - shape (elements_count,) - Change in free length
        /// </summary>
        public double[] DeltaFreeLength { get; set; }

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

        #region Constructor
        /// <summary>
        /// Initialize FEM_Elements with nodes and element properties. All computations will be done in Python.
        /// </summary>
        /// <param name="nodes">FEM_Nodes instance</param>
        /// <param name="type">Element types, shape (elements_count,)</param>
        /// <param name="endNodes">Node indices, shape (elements_count, 2)</param>
        /// <param name="areas">Cross-sections, shape (elements_count, 2) : [A_if_compression, A_if_tension]</param>
        /// <param name="youngs">Young's moduli, shape (elements_count, 2) : [E_if_compression, E_if_tension]</param>
        /// <param name="deltaFreeLength">variation of free Length due to prestressing or form-finding, shape (elements_count,)</param>
        /// <param name="tension">Axial forces, shape (elements_count,)</param>
        /// <exception cref="ArgumentNullException">Thrown when any required parameter is null</exception>
        public FEM_Elements(FEM_Nodes nodes, int[] type, int[,] endNodes, double[,] areas, 
                          double[,] youngs, double[] deltaFreeLength = null, double[] tension = null)
        {
            Nodes = nodes ?? throw new ArgumentNullException(nameof(nodes));
            Type = type ?? throw new ArgumentNullException(nameof(type));
            EndNodes = endNodes ?? throw new ArgumentNullException(nameof(endNodes));
            Areas = areas ?? throw new ArgumentNullException(nameof(areas));
            Youngs = youngs ?? throw new ArgumentNullException(nameof(youngs));
            
            // Set count from end nodes
            Count = EndNodes.GetLength(0);
            
            // Initialize mutable properties with empty arrays
            // These will be populated with values computed in Python
            InitialFreeLength = new double[Count];
            Area = new double[Count];
            Young = new double[Count];
            CurrentLength = new double[Count];
            CurrentFreeLength = new double[Count];
            DeltaFreeLength = deltaFreeLength ?? new double[Count];
            Tension = tension ?? new double[Count];
            Flexibility = new double[Count];
            DirectionCosines = new double[Count, 3];
        }
        #endregion
    }
}