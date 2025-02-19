using System;
using Python.Runtime;
using Muscle.Structure;

namespace Muscle.FEModel
{
    public static class FEM_PythonConverter
    {
        public static FEM_Nodes ConvertToPythonFEMNodes(StructureObj structure)
        {
            var nodes = new FEM_Nodes();
            nodes.RegisterNodes(structure);
            return nodes;
        }

        public static FEM_Elements ConvertToPythonFEMElements(StructureObj structure)
        {
            var elements = new FEM_Elements();
            elements.RegisterElements(structure);
            return elements;
        }

        public static void UpdateStructureFromPythonResults(StructureObj structure, dynamic pythonResults)
        {
            // Update node positions
            for (int i = 0; i < structure.StructuralNodes.Count; i++)
            {
                var node = structure.StructuralNodes[i];
                node.Point.X = pythonResults.NodesCoord[i, 0];
                node.Point.Y = pythonResults.NodesCoord[i, 1];
                node.Point.Z = pythonResults.NodesCoord[i, 2];
            }

            // Update reactions
            for (int i = 0; i < structure.StructuralNodes.Count; i++)
            {
                var node = structure.StructuralNodes[i];
                if (!node.isXFree) node.Reaction.X = pythonResults.ReactionsInit[3 * i];
                if (!node.isYFree) node.Reaction.Y = pythonResults.ReactionsInit[3 * i + 1];
                if (!node.isZFree) node.Reaction.Z = pythonResults.ReactionsInit[3 * i + 2];
            }

            // Update element tensions
            for (int i = 0; i < structure.StructuralElements.Count; i++)
            {
                var element = structure.StructuralElements[i];
                element.Tension = pythonResults.Tension[i];
            }
        }
    }
}
