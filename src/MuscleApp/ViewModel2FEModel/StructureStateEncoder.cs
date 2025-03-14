using MuscleCore.FEModel;
using Muscle.ViewModel;
using System;

namespace Muscle.ViewModel2FEModel
{
    /// <summary>
    /// Converts StructureState instances to FEM_Structure for computational analysis.
    /// </summary>
    public static class StructureStateEncoder
    {
        /// <summary>
        /// Converts a StructureState instance to a FEM_Structure instance.
        /// </summary>
        /// <param name="structure">StructureState instance to convert</param>
        /// <returns>FEM_Structure instance containing all data needed for analysis</returns>
        public static FEM_Structure ToFEM_Structure(StructureState structure)
        {
            if (structure == null)
                throw new ArgumentNullException(nameof(structure), "StructureState cannot be null");
            
            if (structure.Nodes.Count == 0)
                throw new ArgumentException("StructureState must have at least one node", nameof(structure));
            
            if (structure.Elements.Count == 0)
                throw new ArgumentException("StructureState must have at least one element", nameof(structure));
            
            // First convert nodes
            FEM_Nodes femNodes = NodesEncoder.ToFEM_Nodes(structure.Nodes);
            
            // Then convert elements, using the converted nodes
            FEM_Elements femElements = ElementsEncoder.ToFEM_Elements(structure.Elements, femNodes);
            
            // Create the FEM_Structure
            return new FEM_Structure(femNodes, femElements);
        }
        
        /// <summary>
        /// Updates a StructureState instance from a FEM_Structure instance after computational analysis.
        /// </summary>
        /// <param name="structure">StructureState instance to update</param>
        /// <param name="femStructure">FEM_Structure instance containing analysis results</param>
        public static void UpdateFromFEM_Structure(StructureState structure, FEM_Structure femStructure)
        {
            if (structure == null)
                throw new ArgumentNullException(nameof(structure), "StructureState cannot be null");
            
            if (femStructure == null)
                throw new ArgumentNullException(nameof(femStructure), "FEM_Structure cannot be null");
            
            if (structure.NodesCount != femStructure.Nodes.Count)
                throw new ArgumentException("Node count mismatch between StructureState and FEM_Structure");
            
            if (structure.ElementsCount != femStructure.Elements.Count)
                throw new ArgumentException("Element count mismatch between StructureState and FEM_Structure");
            
            // Update nodes first
            NodesEncoder.UpdateFromFEM_Nodes(structure.Nodes, femStructure.Nodes);
            
            // Then update elements
            ElementsEncoder.UpdateFromFEM_Elements(structure.Elements, femStructure.Elements);
        }
    }
}
