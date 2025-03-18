using Rhino.Geometry;
using System;
using System.Collections.Generic;
using MuscleApp.ViewModel;
using MuscleCore.FEModel;

namespace MuscleApp.Converters
{
    /// <summary>
    /// Static class for decoding CoreTruss instances to Truss instances.
    /// </summary>
    public static class TrussDecoder
    {
        /// <summary>
        /// Updates a Truss instance with results from a CoreTruss instance.
        /// </summary>
        /// <param name="original">Truss instance to update</param>
        /// <param name="coreTrussResults">CoreTruss instance containing structure results</param>
        /// <returns>Updated Truss instance</returns>
        public static Truss CopyAndUpdate(Truss original, CoreTruss coreTrussResults)
        {
            if (original == null)
                throw new ArgumentNullException(nameof(original), "Truss cannot be null");
                
            if (coreTrussResults == null)
                throw new ArgumentNullException(nameof(coreTrussResults), "CoreTruss cannot be null");
                
            if (coreTrussResults.Nodes == null || coreTrussResults.Elements == null)
                throw new ArgumentException("CoreTruss must have valid Nodes and Elements", nameof(coreTrussResults));
            
            // Create a copy of the original structure state
            Truss updated = original.Copy();

            // retrieve the results from the computations stored in coreTrussResults
            CoreNodes nodesResults = coreTrussResults.Nodes;
            CoreElements elementsResults = coreTrussResults.Elements;
            
            // Copy and Update original nodes with the nodes results 
            updated.Nodes = NodesDecoder.CopyAndUpdate(original.Nodes, nodesResults);
            
            // Copy and Update original elements with the elements results
            updated.Elements = ElementsDecoder.CopyAndUpdate(original.Elements, elementsResults, updated.Nodes);
            
            // Update equilibrium state
            updated.IsInEquilibrium = coreTrussResults.IsInEquilibrium;

            return updated;
        }
    }
}