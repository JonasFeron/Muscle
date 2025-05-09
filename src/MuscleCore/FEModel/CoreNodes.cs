// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

// PythonNETGrasshopperTemplate

// Copyright <2025> <Jonas Feron>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

using System;
using System.Collections.Generic;

namespace MuscleCore.FEModel
{
    /// <summary>
    /// Data container for CoreNodes. All computations and logic are handled in the Python equivalent class.
    /// This class serves as a pure data transfer object between C# and Python.
    /// </summary>
    public class CoreNodes
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
        public double[,] Residuals { get; set; }
        #endregion

        #region Constructors
        /// <summary>
        /// Minimal constructor that initializes with initial coordinates and DOF.
        /// This constructor matches the Python constructor in fem_nodes.py for testing PyNodesEncoder.
        /// </summary>
        /// <param name="initialCoordinates">[m] - shape (nodes_count, 3) - Initial nodal coordinates</param>
        /// <param name="dof">[-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)</param>
        /// <param name="loads">[N] - shape (nodes_count, 3) - External loads applied to nodes</param>
        /// <param name="displacements">[m] - shape (nodes_count, 3) - Nodal displacements</param>
        /// <param name="reactions">[N] - shape (nodes_count, 3) - Support reactions</param>
        /// <param name="resistingForces">[N] - shape (nodes_count, 3) - Internal resisting forces at nodes</param>
        public CoreNodes(double[,] initialCoordinates, bool[,] dof, double[,]? loads = null, 
                        double[,]? displacements = null, double[,]? reactions = null, double[,]? resistingForces = null)
        {
            // Initialize properties
            InitialCoordinates = initialCoordinates ?? throw new ArgumentNullException(nameof(initialCoordinates));
            DOF = dof ?? throw new ArgumentNullException(nameof(dof));
            Count = initialCoordinates.GetLength(0);
            
            // Initialize mutable properties with default values if null
            Coordinates = new double[Count, 3];
            Loads = loads ?? new double[Count, 3];
            Displacements = displacements ?? new double[Count, 3];
            Reactions = reactions ?? new double[Count, 3];
            ResistingForces = resistingForces ?? new double[Count, 3];
            Residuals = new double[Count, 3];
        }

        /// <summary>
        /// Full constructor for setting all properties. Used when decoding from Python where all values are known.
        /// </summary>
        /// <param name="initialCoordinates">[m] - shape (nodes_count, 3) - Initial nodal coordinates</param>
        /// <param name="coordinates">[m] - shape (nodes_count, 3) - Current nodal coordinates</param>
        /// <param name="dof">[-] - shape (nodes_count, 3) - Degrees of freedom (True if free, False if fixed)</param>
        /// <param name="count">Number of nodes</param>
        /// <param name="loads">[N] - shape (nodes_count, 3) - External loads applied to nodes</param>
        /// <param name="displacements">[m] - shape (nodes_count, 3) - Nodal displacements</param>
        /// <param name="reactions">[N] - shape (nodes_count, 3) - Support reactions</param>
        /// <param name="resistingForces">[N] - shape (nodes_count, 3) - Internal resisting forces at nodes</param>
        /// <param name="residuals">[N] - shape (nodes_count, 3) - Out of balance loads</param>
        public CoreNodes(
            double[,] initialCoordinates,
            double[,] coordinates,
            bool[,] dof,
            int count,
            double[,] loads,
            double[,] displacements,
            double[,] reactions,
            double[,] resistingForces,
            double[,] residuals)
        {
            InitialCoordinates = initialCoordinates ?? throw new ArgumentNullException(nameof(initialCoordinates));
            Coordinates = coordinates ?? throw new ArgumentNullException(nameof(coordinates));
            DOF = dof ?? throw new ArgumentNullException(nameof(dof));
            Count = count;
            Loads = loads ?? throw new ArgumentNullException(nameof(loads));
            Displacements = displacements ?? throw new ArgumentNullException(nameof(displacements));
            Reactions = reactions ?? throw new ArgumentNullException(nameof(reactions));
            ResistingForces = resistingForces ?? throw new ArgumentNullException(nameof(resistingForces));
            Residuals = residuals ?? throw new ArgumentNullException(nameof(residuals));
        }
        #endregion

        #region Methods

        #endregion
    }
}