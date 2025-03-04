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
                    return objectType.Name == "FEM_Nodes";
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
                    // Get Python object as dynamic
                    dynamic py = pyObj.As<dynamic>();

                    // Convert all arrays using the helper
                    var initialCoords = DecoderHelper.ToCSArray2D(py.initial_coordinates);
                    var coordinates = DecoderHelper.ToCSArray2D(py.coordinates);
                    var dofs = DecoderHelper.ToCSBoolArray2D(py.dof);
                    var loads = DecoderHelper.ToCSArray2D(py.loads);
                    var displacements = DecoderHelper.ToCSArray2D(py.displacements);
                    var reactions = DecoderHelper.ToCSArray2D(py.reactions);
                    var resistingForces = DecoderHelper.ToCSArray2D(py.resisting_forces);
                    var residual = DecoderHelper.ToCSArray2D(py.residual);

                    // Create nodes object with all properties
                    var nodes = new FEM_Nodes(
                        initialCoordinates: initialCoords,
                        coordinates: coordinates,
                        dof: dofs,
                        count: (int)py.count,
                        fixationsCount: (int)py.fixations_count,
                        loads: loads,
                        displacements: displacements,
                        reactions: reactions,
                        resistingForces: resistingForces,
                        residual: residual
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
