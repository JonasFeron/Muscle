using MuscleCore.TwinModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class TwinStructureEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(TwinStructure);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var structure = (TwinStructure)obj;
            using (Py.GIL())
            {
                dynamic pyModel = Py.Import("twin_model.twin_structure");

                return pyModel.Twin_Structure(
                    structure.Nodes,
                    structure.Elements,
                    structure.Additional,
                    structure.Applied,
                    structure.InitialNodesResults,
                    structure.InitialElementsResults
                );
            }
        }
    }
}
