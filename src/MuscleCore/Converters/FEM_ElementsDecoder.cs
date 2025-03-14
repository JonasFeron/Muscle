using MuscleCore.FEModel;
using Python.Runtime;

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
                    var endNodes = DecoderHelper.ToCSIntArray2D(py.end_nodes);
                    var initialFreeLength = py.initial_free_length.tolist().As<double[]>();
                    var areas = DecoderHelper.ToCSArray2D(py.areas);
                    var youngs = DecoderHelper.ToCSArray2D(py.youngs);
                    var area = py.area.tolist().As<double[]>();
                    var young = py.young.tolist().As<double[]>();
                    var currentLength = py.current_length.tolist().As<double[]>();
                    var currentFreeLength = py.current_free_length.tolist().As<double[]>();
                    var deltaFreeLength = py.delta_free_length.tolist().As<double[]>();
                    var tension = py.tension.tolist().As<double[]>();
                    var flexibility = py.flexibility.tolist().As<double[]>();
                    var directionCosines = DecoderHelper.ToCSArray2D(py.direction_cosines);

                    // Create elements object with all properties
                    var elements = new FEM_Elements(
                        nodes: nodes,
                        type: type,
                        endNodes: endNodes,
                        initialFreeLength: initialFreeLength,
                        count: (int)py.count,
                        areas: areas,
                        youngs: youngs,
                        area: area,
                        young: young,
                        currentLength: currentLength,
                        currentFreeLength: currentFreeLength,
                        deltaFreeLength: deltaFreeLength,
                        tension: tension,
                        flexibility: flexibility,
                        directionCosines: directionCosines
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
