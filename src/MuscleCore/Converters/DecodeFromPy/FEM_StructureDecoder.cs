using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class FEM_StructureDecoder : IPyObjectDecoder
    {
        private readonly FEM_NodesDecoder _nodesDecoder;
        private readonly FEM_ElementsDecoder _elementsDecoder;

        public FEM_StructureDecoder()
        {
            _nodesDecoder = new FEM_NodesDecoder();
            _elementsDecoder = new FEM_ElementsDecoder();
        }

        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(FEM_Structure))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "FEM_Structure";

                }
                catch
                {
                    return false;
                }
            }
        }

        public bool TryDecode<T>(PyObject pyObj, out T? value)
        {
            value = default;
            if (typeof(T) != typeof(FEM_Structure))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Get nodes and elements objects
                    var femElements = py.elements.As<FEM_Elements>();
                    var femNodes = femElements.Nodes;
                    bool isInEquilibrium = py.is_in_equilibrium.As<bool>();

                    // Create structure with all properties
                    var structure = new FEM_Structure(
                        nodes: femNodes,
                        elements: femElements,
                        isInEquilibrium: isInEquilibrium
                    );

                    value = (T)(object)structure;
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in TryDecode: {ex.Message}\n{ex.StackTrace}");
                    return false;
                }
            }
        }
    }
}
