using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class PyTrussDecoder : IPyObjectDecoder
    {
        private readonly PyNodesDecoder _nodesDecoder;
        private readonly PyElementsDecoder _elementsDecoder;

        public PyTrussDecoder()
        {
            _nodesDecoder = new PyNodesDecoder();
            _elementsDecoder = new PyElementsDecoder();
        }

        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(CoreTruss))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "PyTruss";

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
            if (typeof(T) != typeof(CoreTruss))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Get nodes and elements objects
                    var femElements = py.elements.As<CoreElements>();
                    var femNodes = femElements.Nodes;
                    
                    // Call the is_in_equilibrium method with default parameters
                    bool isInEquilibrium = py.is_in_equilibrium().As<bool>();

                    // Create structure with all properties
                    var structure = new CoreTruss(
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
