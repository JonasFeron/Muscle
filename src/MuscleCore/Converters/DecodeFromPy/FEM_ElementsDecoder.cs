using MuscleCore.FEModel;
using Python.Runtime;
using static MuscleCore.Converters.DecoderHelper;

namespace MuscleCore.Converters
{
    public class FEM_ElementsDecoder : IPyObjectDecoder
    {
        private readonly FEM_NodesDecoder _nodesDecoder;

        public FEM_ElementsDecoder()
        {
            _nodesDecoder = new FEM_NodesDecoder();
        }

        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(FEM_Elements))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "FEM_Elements";
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
            if (typeof(T) != typeof(FEM_Elements))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Debug: Check the type
                    Console.WriteLine($"Type of py.type: {py.type.GetType()}");
                    Console.WriteLine($"Python type: {py.type.__class__.__name__}");

                    // First decode the nodes object
                    var nodes = py.nodes.As<FEM_Nodes>();

                    // Convert all arrays using the helper
                    dynamic numpy = Py.Import("numpy");
                    var type = py.type.tolist().As<int[]>();
                    var endNodes = AsInt2dArray(py.end_nodes);
                    var youngs = As2dArray(py.youngs);
                    var area = py.area.tolist().As<double[]>();
                    var freeLength = py.free_length.tolist().As<double[]>();
                    var tension = py.tension.tolist().As<double[]>();


                    // Create elements object with all properties
                    var elements = new FEM_Elements(
                        nodes: nodes,
                        type: type,
                        endNodes: endNodes,
                        youngs: youngs,
                        area: area,
                        freeLength: freeLength,
                        tension: tension
                    );

                    value = (T)(object)elements;
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
