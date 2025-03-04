using System;

namespace MuscleCore.FEModel
{
    /// <summary>
    /// Pure data container for FEM_Structure, combining nodes and elements.
    /// All computations are handled in the Python equivalent (fem_structure.py).
    /// </summary>
    public class FEM_Structure
    {
        /// <summary>
        /// Get or set the FEM_Nodes instance
        /// </summary>
        public FEM_Nodes Nodes { get; set; }

        /// <summary>
        /// Get or set the FEM_Elements instance
        /// </summary>
        public FEM_Elements Elements { get; set; }

        /// <summary>
        /// Get or set whether the structure is in equilibrium.
        /// If loads magnitude is 1000N, the structure is considered in equilibrium 
        /// if the residual magnitude is inferior to 1e-4 * 1000N = 0.1 N
        /// </summary>
        public bool IsInEquilibrium { get; set; }

        /// <summary>
        /// Minimal constructor that validates node references
        /// </summary>
        public FEM_Structure(FEM_Nodes nodes, FEM_Elements elements)
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
        public FEM_Structure(
            FEM_Nodes nodes,
            FEM_Elements elements,
            bool isInEquilibrium)
            : this(nodes, elements)  // Call minimal constructor for validation
        {
            IsInEquilibrium = isInEquilibrium;
        }
    }
}
