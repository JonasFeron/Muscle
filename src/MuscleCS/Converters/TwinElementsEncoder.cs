using MuscleCore.TwinModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class TwinElementsEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(TwinElements);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var elements = (TwinElements)obj;
            using (Py.GIL())
            {
                dynamic pyModel = Py.Import("twin_model.twin_elements");

                return pyModel.Twin_Elements(
                    elements.Type,
                    elements.EndNodes,
                    elements.Areas,
                    elements.YoungModuli
                );
            }
        }
    }
}
