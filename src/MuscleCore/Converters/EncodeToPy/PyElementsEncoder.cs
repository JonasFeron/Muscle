using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class PyElementsEncoder : IPyObjectEncoder
    {

        public bool CanEncode(Type type)
        {
            return type == typeof(CoreElements);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var elements = (CoreElements)obj;
            using (Py.GIL())
            {
                dynamic musclepy = Py.Import("MusclePy");

                return musclepy.PyElements(
                    nodes: elements.Nodes.ToPython(),
                    type: elements.Type,
                    end_nodes: elements.EndNodes,
                    area: elements.Area,
                    youngs: elements.Youngs,
                    free_length: elements.FreeLength,
                    tension: elements.Tension
                );
            }
        }
    }
}
