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
                dynamic musclepy = Py.Import("MusclePy");

                // Convert nodes first and reuse the same instance
                var pythonNodes = structure.Nodes.ToPython();
                var elementsEncoder = new FEM_ElementsEncoder(pythonNodes);
                return musclepy.FEM_Structure(
                    nodes: pythonNodes,
                    elements: elementsEncoder.TryEncode(structure.Elements)
                );
            }
        }
    }
}
