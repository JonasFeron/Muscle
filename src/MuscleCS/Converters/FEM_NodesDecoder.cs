using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class FEM_NodesDecoder : IPyObjectDecoder
    {
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(FEM_Nodes))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get the module where FEM_Nodes is defined
                    dynamic musclepy = Py.Import("MusclePy");
                    var femNodesType = ((PyObject)musclepy.FEM_Nodes).GetPythonType();
                    return objectType == femNodesType;
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
            if (typeof(T) != typeof(FEM_Nodes))
                return false;

            using (Py.GIL())
            {
                try
                {
                    dynamic py = pyObj.As<dynamic>();

                    var nodes = new FEM_Nodes(
                        py.initial_coordinates.As<double[,]>(),
                        py.dof.As<bool[,]>(),
                        py.loads.As<double[,]>(),
                        py.displacements.As<double[,]>(),
                        py.reactions.As<double[,]>(),
                        py.resisting_forces.As<double[,]>()
                    );

                    value = (T)(object)nodes;
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
