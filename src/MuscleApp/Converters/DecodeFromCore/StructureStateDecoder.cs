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
        /// Updates a StructureState instance with data from a FEM_Structure instance.
        /// </summary>
        /// <param name="structureState">StructureState instance to update</param>
        /// <param name="femStructure">FEM_Structure instance containing structure data</param>
        /// <returns>Updated StructureState instance</returns>
        public static StructureState CopyAndUpdateFrom(StructureState structureState, FEM_Structure femStructure)
        {
            if (structureState == null)
                throw new ArgumentNullException(nameof(structureState), "StructureState cannot be null");
                
            if (femStructure == null)
                throw new ArgumentNullException(nameof(femStructure), "FEM_Structure cannot be null");
                
            if (femStructure.Nodes == null || femStructure.Elements == null)
                throw new ArgumentException("FEM_Structure must have valid Nodes and Elements", nameof(femStructure));
            
            // Create a copy of the original structure state
            StructureState updatedStructureState = structureState.Copy();
            
            // Update nodes
            updatedStructureState.Nodes = NodesDecoder.CopyAndUpdateFrom(structureState.Nodes, femStructure.Nodes);
            
            // Update elements using the updated nodes
            updatedStructureState.Elements = ElementsDecoder.CopyAndUpdateFrom(structureState.Elements, femStructure.Elements, updatedStructureState.Nodes);
            
            // Update equilibrium state
            updatedStructureState.IsInEquilibrium = femStructure.IsInEquilibrium;

            return updatedStructureState;
        }
    }
}