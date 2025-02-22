using MuscleCore.TwinModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class TwinNodesEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(TwinNodes);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var nodes = (TwinNodes)obj;
            using (Py.GIL())
            {
                dynamic pyModel = Py.Import("twin_model.twin_nodes");

                return pyModel.Twin_Nodes(
                    nodes.Coordinates,
                    nodes.IsDOFfree
                );
            }
        }
    }
}
