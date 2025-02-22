using MuscleCore.TwinModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class TwinElementsResultsEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(TwinElementsResults);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var results = (TwinElementsResults)obj;
            using (Py.GIL())
            {
                dynamic pyModel = Py.Import("twin_model.twin_elements_results");

                return pyModel.Twin_ElementsResults(
                    results.Tension,
                    results.ElasticElongation
                );
            }
        }
    }
}
