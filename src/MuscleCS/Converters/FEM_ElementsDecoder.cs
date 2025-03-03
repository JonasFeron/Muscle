using MuscleCore.FEModel;
using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public class FEM_ElementsDecoder : IPyObjectDecoder
    {
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
                    dynamic py = pyObj.As<dynamic>();
                    
                    // Get the nodes object first
                    var nodes = py.nodes.As<FEM_Nodes>();

                    // Convert numpy arrays to C# arrays
                    var type = ((PyObject)py.type).As<int[]>();
                    var endNodes = DecoderHelper.ToCSArray2D(py.end_nodes);
                    var areas = DecoderHelper.ToCSArray2D(py.areas);
                    var youngs = DecoderHelper.ToCSArray2D(py.youngs);
                    var deltaFreeLength = ((PyObject)py.delta_free_length).As<double[]>();
                    var tension = ((PyObject)py.tension).As<double[]>();

                    // Create FEM_Elements instance with initial properties
                    var elements = new FEM_Elements(
                        nodes: nodes,
                        type: type,
                        endNodes: endNodes,
                        areas: areas,
                        youngs: youngs,
                        deltaFreeLength: deltaFreeLength,
                        tension: tension
                    );

                    // Set computed properties from Python
                    elements.InitialFreeLength = ((PyObject)py.initial_free_length).As<double[]>();
                    elements.Area = ((PyObject)py.area).As<double[]>();
                    elements.Young = ((PyObject)py.young).As<double[]>();
                    elements.CurrentLength = ((PyObject)py.current_length).As<double[]>();
                    elements.CurrentFreeLength = ((PyObject)py.current_free_length).As<double[]>();
                    elements.Flexibility = ((PyObject)py.flexibility).As<double[]>();
                    elements.DirectionCosines = DecoderHelper.ToCSArray2D(py.direction_cosines);

                    value = (T)(object)elements;
                    return true;
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Error in TryDecode: {ex.Message}");
                    return false;
                }
            }
        }
    }
}
