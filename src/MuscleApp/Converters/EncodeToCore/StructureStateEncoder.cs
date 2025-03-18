using MuscleCore.FEModel;
using MuscleApp.ViewModel;
using System;
using System.Collections.Generic;
using static MuscleApp.Converters.NodesEncoder;
using static MuscleApp.Converters.ElementsEncoder;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Converts StructureState instances to CoreTruss for computational analysis.
    /// </summary>
    public static class StructureStateEncoder
    {
        /// <summary>
        /// Converts a StructureState instance to a CoreTruss instance for computational analysis.
        /// </summary>
        /// <param name="structure">StructureState instance to convert</param>
        /// <returns>CoreTruss instance containing all data needed for analysis</returns>
        public static CoreTruss ToCore(StructureState structure)
        {
            if (structure == null)
                throw new ArgumentNullException(nameof(structure), "StructureState cannot be null");
            
            if (structure.Nodes.Count == 0)
                throw new ArgumentException("StructureState must have at least one node", nameof(structure));
            
            if (structure.Elements.Count == 0)
                throw new ArgumentException("StructureState must have at least one element", nameof(structure));
            
            // First convert nodes
            List<Node> nodes = structure.Nodes;
            CoreNodes coreNodes = ToCoreNodes(nodes);
            
            // Then convert elements, using the converted nodes
            List<Element> elements = structure.Elements;
            CoreElements coreElements = ToCoreElements(elements, coreNodes);
            
            // Create the CoreTruss for computational analysis
            return new CoreTruss(coreNodes, coreElements);
        }
    }
}
