using System;

namespace MuscleCore.FEModel
{
    /// <summary>
    /// Pure data container for CoreTruss, combining nodes and elements.
    /// All computations are handled in the Python equivalent (fem_structure.py).
    /// </summary>
    public class CoreTruss
    {
        /// <summary>
        /// Get or set the CoreNodes instance
        /// </summary>
        public CoreNodes Nodes { get; set; }

        /// <summary>
        /// Get or set the CoreElements instance
        /// </summary>
        public CoreElements Elements { get; set; }

        /// <summary>
        /// Get or set whether the structure is in equilibrium.
        /// If loads magnitude is 1000N, the structure is considered in equilibrium 
        /// if the residual magnitude is inferior to 1e-4 * 1000N = 0.1 N
        /// </summary>
        public bool IsInEquilibrium { get; set; }

        /// <summary>
        /// Minimal constructor that validates node references
        /// </summary>
        public CoreTruss(CoreNodes nodes, CoreElements elements)
        {
            Nodes = nodes ?? throw new ArgumentNullException(nameof(nodes));
            Elements = elements ?? throw new ArgumentNullException(nameof(elements));

            if (Elements.Nodes != nodes)
            {
                throw new ArgumentException("Elements must reference the same nodes instance", nameof(elements));
            }
        }

        /// <summary>
        /// Full constructor for setting all properties, used when decoding from Python
        /// </summary>
        public CoreTruss(
            CoreNodes nodes,
            CoreElements elements,
            bool isInEquilibrium)
            : this(nodes, elements)  // Call minimal constructor for validation
        {
            IsInEquilibrium = isInEquilibrium;
        }
    }
}
