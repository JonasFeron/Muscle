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

        public PyObject TryEncode(object? obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var structure = (FEM_Structure)obj;
            using (Py.GIL())
            {
                try
                {
                    dynamic musclepy = Py.Import("MusclePy");
                    dynamic pyElements = structure.Elements.ToPython();
                    dynamic pyNodes = pyElements.nodes;

                    return musclepy.FEM_Structure(
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
