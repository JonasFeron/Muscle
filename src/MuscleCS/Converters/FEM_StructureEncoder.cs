using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class FEM_StructureEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(FEM_Structure);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var structure = (FEM_Structure)obj;
            using (Py.GIL())
            {
                dynamic fem_structure = Py.Import("femodel.fem_structure");

                // Convert nodes first and reuse the same instance
                var pythonNodes = structure.Nodes.ToPython();
                var elementsEncoder = new FEM_ElementsEncoder(pythonNodes);
                return fem_structure.FEM_Structure(
                    nodes: pythonNodes,
                    elements: elementsEncoder.TryEncode(structure.Elements)
                );
            }
        }
    }
}
