using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class FEM_StructureDecoder : IPyObjectDecoder
    {
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
                    dynamic py = pyObj.As<dynamic>();

                    // Get nodes and elements objects
                    var nodes = py.nodes.As<FEM_Nodes>();
                    var elements = py.elements.As<FEM_Elements>();

                    // Create FEM_Structure instance
                    var structure = new FEM_Structure(nodes, elements);

                    // Set computed properties from Python
                    structure.IsInEquilibrium = py.is_in_equilibrium;

                    value = (T)(object)structure;
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
