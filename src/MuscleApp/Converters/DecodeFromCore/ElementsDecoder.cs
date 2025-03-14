

        /// <summary>
        /// Updates this Element instance with data from a FEM_Elements instance and element index.
        /// </summary>
        /// <param name="femElements">FEM_Elements instance containing element data</param>
        /// <param name="elementIndex">Index of the element in the FEM_Elements arrays</param>
        /// <param name="nodes">List of Node instances to get coordinates for creating the Line</param>
        public void CopyAndUpdateFrom(MuscleCore.FEModel.FEM_Elements femElements, int elementIndex, List<Node> nodes)
        {
            if (femElements == null)
                throw new ArgumentNullException(nameof(femElements), "FEM_Elements cannot be null");
                
            if (elementIndex < 0 || elementIndex >= femElements.Count)
                throw new ArgumentOutOfRangeException(nameof(elementIndex), "Element index is out of range");
                
            if (nodes == null || nodes.Count == 0)
                throw new ArgumentException("Nodes collection cannot be null or empty", nameof(nodes));
            
            // Set element index
            Idx = elementIndex;
            
            // Set element type (-1 for struts, 1 for cables, 0 for both)
            Type = femElements.Type[elementIndex];
            
            // Set end nodes indices
            int node0Index = femElements.EndNodes[elementIndex, 0];
            int node1Index = femElements.EndNodes[elementIndex, 1];
            EndNodes = new List<int> { node0Index, node1Index };
            
            // Create line from node coordinates
            if (node0Index < nodes.Count && node1Index < nodes.Count)
            {
                Line = new Line(nodes[node0Index].Point, nodes[node1Index].Point);
            }
            else
            {
                throw new ArgumentException("Node indices in FEM_Elements are out of range for the provided nodes collection");
            }
            
            // Set cross-section area
            CS = new CS_Circular(femElements.Area[elementIndex] * 2, femElements.Area[elementIndex]);
            
            // Set material properties (Young's moduli for compression and tension)
            Material = new BilinearMaterial(
                "Material from FEM_Elements", 
                femElements.Youngs[elementIndex, 0], // Young's modulus for compression
                femElements.Youngs[elementIndex, 1], // Young's modulus for tension
                -1e9, // Default compressive yield strength
                1e9,  // Default tensile yield strength
                7850  // Default density (steel)
            );
            
            // Set free length and tension
            FreeLength = femElements.FreeLength[elementIndex];
            Tension = femElements.Tension[elementIndex];
            
            // Set default buckling law and factor
            BucklingLaw = "Yielding";
            kb = 1.0;
            
            // Set name
            Name = $"Element {Idx}";
        }
