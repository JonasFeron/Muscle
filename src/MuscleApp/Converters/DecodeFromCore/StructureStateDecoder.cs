using Rhino.Geometry;
using System;
using System.Collections.Generic;
using MuscleApp.ViewModel;
using MuscleCore.FEModel;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Static class for decoding FEM_Structure instances to StructureState instances.
    /// </summary>
    public static class StructureStateDecoder
    {
        /// <summary>
        /// Updates a StructureState instance with results from a FEM_Structure instance.
        /// </summary>
        /// <param name="original">StructureState instance to update</param>
        /// <param name="femResults">FEM_Structure instance containing structure data</param>
        /// <returns>Updated StructureState instance</returns>
        public static StructureState CopyAndUpdate(StructureState original, FEM_Structure femResults)
        {
            if (original == null)
                throw new ArgumentNullException(nameof(original), "StructureState cannot be null");
                
            if (femResults == null)
                throw new ArgumentNullException(nameof(femResults), "FEM_Structure cannot be null");
                
            if (femResults.Nodes == null || femResults.Elements == null)
                throw new ArgumentException("FEM_Structure must have valid Nodes and Elements", nameof(femResults));
            
            // Create a copy of the original structure state
            StructureState updated = original.Copy();

            // retrieve the results from the computations stored in femResults
            FEM_Nodes nodesResults = femResults.Nodes;
            FEM_Elements elementsResults = femResults.Elements;
            
            // Copy and Update original nodes with the nodes results 
            updated.Nodes = NodesDecoder.CopyAndUpdate(original.Nodes, nodesResults);
            
            // Copy and Update original elements with the elements results
            updated.Elements = ElementsDecoder.CopyAndUpdate(original.Elements, elementsResults, updated.Nodes);
            
            // Update equilibrium state
            updated.IsInEquilibrium = femResults.IsInEquilibrium;

            return updated;
        }
    }
}