using MuscleCore.FEModel;
using Python.Runtime;

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

                    var elements = new FEM_Elements(
                        py.nodes.As<FEM_Nodes>(),
                        py.type.As<int[]>(),
                        py.end_nodes.As<int[,]>(),
                        py.areas.As<double[,]>(),
                        py.youngs.As<double[,]>(),
                        py.delta_free_length.As<double[]>(),
                        py.tension.As<double[]>()
                    );

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
