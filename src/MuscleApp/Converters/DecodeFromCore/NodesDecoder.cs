        /// <summary>
        /// Updates this Node instance with data from a FEM_Nodes instance and node index.
        /// </summary>
        /// <param name="femNodes">FEM_Nodes instance containing node data</param>
        /// <param name="nodeIndex">Index of the node in the FEM_Nodes arrays</param>
        public Node CopyAndUpdateFrom(FEM_Nodes femNodes, int nodeIndex)
        {
            Node updatedNode = this.Copy();
            
            if (femNodes == null)
                throw new ArgumentNullException(nameof(femNodes), "FEM_Nodes cannot be null");
                
            if (nodeIndex < 0 || nodeIndex >= femNodes.Count)
                throw new ArgumentOutOfRangeException(nameof(nodeIndex), "Node index is out of range");
                
            // Set node index
            Idx = nodeIndex;
            
            // Create point from initial coordinates
            Point = new Point3d(
                femNodes.InitialCoordinates[nodeIndex, 0],
                femNodes.InitialCoordinates[nodeIndex, 1],
                femNodes.InitialCoordinates[nodeIndex, 2]
            );
            
            // Set DOF constraints (true = free, false = fixed)
            isXFree = femNodes.DOF[nodeIndex, 0];
            isYFree = femNodes.DOF[nodeIndex, 1];
            isZFree = femNodes.DOF[nodeIndex, 2];
            
            // Set loads
            Loads = new Vector3d(
                femNodes.Loads[nodeIndex, 0],
                femNodes.Loads[nodeIndex, 1],
                femNodes.Loads[nodeIndex, 2]
            );
            
            // Set reactions
            Reactions = new Vector3d(
                femNodes.Reactions[nodeIndex, 0],
                femNodes.Reactions[nodeIndex, 1],
                femNodes.Reactions[nodeIndex, 2]
            );
            
            // Calculate residuals from loads, reactions, and resisting forces
            Residuals = new Vector3d(
                Loads.X + Reactions.X - femNodes.ResistingForces[nodeIndex, 0],
                Loads.Y + Reactions.Y - femNodes.ResistingForces[nodeIndex, 1],
                Loads.Z + Reactions.Z - femNodes.ResistingForces[nodeIndex, 2]
            );
            
            // Set displacements if available
            if (femNodes.Displacements != null)
            {
                //Displacements = new Vector3d(
                //    femNodes.Displacements[nodeIndex, 0],
                //    femNodes.Displacements[nodeIndex, 1],
                //    femNodes.Displacements[nodeIndex, 2]
                //);
            }
        }