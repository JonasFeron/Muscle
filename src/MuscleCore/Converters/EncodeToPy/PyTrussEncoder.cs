using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class PyTrussEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(CoreTruss);
        }

        public PyObject? TryEncode(object? obj)
        {
            if (obj == null || !CanEncode(obj.GetType()))
                return null;

            var structure = (CoreTruss)obj;
            using (Py.GIL())
            {
                try
                {
                    dynamic musclepy = Py.Import("MusclePy");
                    dynamic pyElements = structure.Elements.ToPython();
                    dynamic pyNodes = pyElements.nodes;

                    return musclepy.PyTruss(
                        nodes: pyNodes,
                        elements: pyElements
                    );
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in TryEncode: {ex.Message}\n{ex.StackTrace}");
                    return null;
                }
            }
        }
    }
}
