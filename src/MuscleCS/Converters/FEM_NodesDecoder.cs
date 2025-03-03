using MuscleCore.FEModel;
using Python.Runtime;
using System.Runtime.InteropServices;
using MuscleCore.Converters.Helpers;

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
                    dynamic py = pyObj.As<dynamic>();
                    
                    // Convert numpy arrays to C# arrays using DecoderHelper
                    var initialCoordinates = DecoderHelper.ToCSArray2D(py.initial_coordinates);
                    var dof = DecoderHelper.ToCSBoolArray2D(py.dof);
                    var loads = DecoderHelper.ToCSArray2D(py.loads);
                    var displacements = DecoderHelper.ToCSArray2D(py.displacements);
                    var reactions = DecoderHelper.ToCSArray2D(py.reactions);
                    var resistingForces = DecoderHelper.ToCSArray2D(py.resisting_forces);

                    // Create FEM_Nodes instance with initial properties
                    var nodes = new FEM_Nodes(
                        initialCoordinates: initialCoordinates,
                        dof: dof,
                        loads: loads,
                        displacements: displacements,
                        reactions: reactions,
                        resistingForces: resistingForces
                    );

                    // Set computed properties from Python
                    nodes.Coordinates = DecoderHelper.ToCSArray2D(py.coordinates);
                    nodes.Residual = DecoderHelper.ToCSArray2D(py.residual);

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
