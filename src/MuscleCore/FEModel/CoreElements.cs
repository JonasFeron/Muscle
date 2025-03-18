using System;
using System.Collections.Generic;
using System.Linq;

namespace MuscleCore.FEModel
{
    /// <summary>
    /// Data container for Elements. All computations and logic are handled in the Python equivalent class.
    /// This class serves as a pure data transfer object between C# and Python.
    /// </summary>
    public class CoreElements
    {
        #region Properties
        /// <summary>
        /// CoreNodes instance containing nodes data
        /// </summary>
        public CoreNodes Nodes { get; set; }

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
        /// [m] - shape (elements_count,) - Free length of the elements
        /// </summary>
        public double[] FreeLength { get; set; }

        /// <summary>
        /// [N] - shape (elements_count,) - Axial force (positive in tension)
        /// </summary>
        public double[] Tension { get; set; }

        #endregion

        #region Constructors
        /// <summary>
        /// Minimal constructor that initializes with required data.
        /// This constructor matches the Python constructor in fem_elements.py for testing PyElementsEncoder.
        /// This constructor is also used when decoding from Python where all values are known.
        /// </summary>
        /// <param name="nodes">CoreNodes instance containing node data</param>
        /// <param name="type">[-] - shape (elements_count,) - Element types (-1: strut, 1: cable)</param>
        /// <param name="endNodes">[-] - shape (elements_count, 2) - Element-node connectivity indices</param>
        /// <param name="area">[mm²] - shape (elements_count,) - Cross-section area of elements</param>
        /// <param name="youngs">[MPa] - shape (elements_count, 2) - Young's moduli for compression and tension</param>
        /// <param name="freeLength">[m] - shape (elements_count,) - Free length of the elements</param>
        /// <param name="tension">[N] - shape (elements_count,) - Axial force (positive in tension)</param>
        public CoreElements(CoreNodes nodes, int[] type = null, int[,] endNodes = null, double[] area = null, 
                          double[,] youngs = null, double[] freeLength = null, double[] tension = null)
        {
            Nodes = nodes ?? throw new ArgumentNullException(nameof(nodes));
            Type = type ?? new int[0];
            EndNodes = endNodes ?? new int[0, 2];
            Count = EndNodes.GetLength(0);
            Area = area ?? new double[Count];
            Youngs = youngs ?? new double[Count, 2];
            FreeLength = freeLength ?? new double[Count];
            Tension = tension ?? new double[Count];
        }

        #endregion
    }
}