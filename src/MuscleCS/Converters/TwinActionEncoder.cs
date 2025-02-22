using MuscleCore.TwinModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class TwinActionEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(TwinActions);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var actions = (TwinActions)obj;
            using (Py.GIL())
            {
                // Import the Python module containing the Twin_Actions class
                dynamic pyModel = Py.Import("twin_model.twin_actions");

                // Create a new instance of Twin_Actions with our C# data
                return pyModel.Twin_Actions(
                    actions.Loads,
                    actions.Delta_FreeLengths
                );
            }
        }
    }
}
