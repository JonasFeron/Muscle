using MuscleCore.TwinModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class TwinNodesResultsEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(TwinNodesResults);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var results = (TwinNodesResults)obj;
            using (Py.GIL())
            {
                dynamic pyModel = Py.Import("twin_model.twin_nodes_results");

                var pyResults = pyModel.Twin_NodesResults();
                pyResults.displacements = results.Displacements;
                pyResults.residual = results.Residual;
                pyResults.reactions = results.Reactions;
                return pyResults;
            }
        }
    }
}
