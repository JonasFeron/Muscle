using MuscleCore.FEModel;
using Python.Runtime;
using static MuscleCore.Converters.DecoderHelper;

namespace MuscleCore.Converters
{
    public class PyNodesDecoder : IPyObjectDecoder
    {
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(CoreNodes))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "PyNodes" || objectType.Name == "PyNodesDR";
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
            if (typeof(T) != typeof(CoreNodes))
                return false;

            using (Py.GIL())
            {
                try
                {
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Convert all arrays using the helper
                    var initialCoords = As2dArray(py.initial_coordinates);
                    var coordinates = As2dArray(py.coordinates);
                    var dofs = AsBool2dArray(py.dof);
                    var loads = As2dArray(py.loads);
                    var displacements = As2dArray(py.displacements);
                    var reactions = As2dArray(py.reactions);
                    var resistingForces = As2dArray(py.resisting_forces);
                    var residuals = As2dArray(py.residuals);

                    // Create nodes object with all properties
                    var nodes = new CoreNodes(
                        initialCoordinates: initialCoords,
                        coordinates: coordinates,
                        dof: dofs,
                        count: (int)py.count,
                        loads: loads,
                        displacements: displacements,
                        reactions: reactions,
                        resistingForces: resistingForces,
                        residuals: residuals
                    );

                    value = (T)(object)nodes;
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
