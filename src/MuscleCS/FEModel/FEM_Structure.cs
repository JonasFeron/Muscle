using System;
using System.Linq;

namespace MuscleCore.FEModel
{
    public class FEM_Structure
    {
        #region Properties
        /// <summary>
        /// Get the FEM_Nodes instance
        /// </summary>
        public FEM_Nodes Nodes { get; }

        /// <summary>
        /// Get the FEM_Elements instance
        /// </summary>
        public FEM_Elements Elements { get; }

        /// <summary>
        /// Check if the structure is in equilibrium.
        /// If loads magnitude is 1000N, the structure is considered in equilibrium 
        /// if the residual magnitude is inferior to 1e-4 * 1000N = 0.1 N
        /// </summary>
        public bool IsInEquilibrium { get; set; }


        // /// <summary>
        // /// Relative precision for equilibrium check
        // /// </summary>
        // private readonly double _relativePrecision = 1e-4;
        #endregion

        #region Constructor
        /// <summary>
        /// Initialize FEM_Structure with nodes and elements. All computations will be done in Python.
        /// </summary>
        /// <param name="nodes">FEM_Nodes instance containing nodal data</param>
        /// <param name="elements">FEM_Elements instance that must reference the same nodes instance</param>
        /// <exception cref="ArgumentNullException">Thrown when either parameter is null</exception>
        /// <exception cref="ArgumentException">Thrown when elements reference different nodes instance</exception>
        public FEM_Structure(FEM_Nodes nodes, FEM_Elements elements)
        {
            Nodes = nodes ?? throw new ArgumentNullException(nameof(nodes));
            Elements = elements ?? throw new ArgumentNullException(nameof(elements));

            if (Elements.Nodes != nodes)
            {
                throw new ArgumentException("Elements must reference the same nodes instance", nameof(elements));
            }
        }
        #endregion
    }
}
