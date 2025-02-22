using MuscleCore.TwinModel;
using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public class TwinStructureResultsDecoder : IPyObjectDecoder
    {
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(TwinStructureResults))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "Twin_StructureResults";
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
            if (typeof(T) != typeof(TwinStructureResults))
                return false;

            using (Py.GIL())
            {
                try
                {
                    dynamic py = pyObj.As<dynamic>();
                    
                    // Create a new TwinStructureResults
                    var results = new TwinStructureResults();
                    results.Total = py.total.As<TwinActions>();
                    results.TotalNodes = py.total_nodes.As<TwinNodesResults>();
                    results.TotalElements = py.total_elements.As<TwinElementsResults>();


                    // // Convert each component using their respective decoders
                    // var actionDecoder = new TwinActionDecoder();
                    // var nodesResultsDecoder = new TwinNodesResultsDecoder();
                    // var elementsResultsDecoder = new TwinElementsResultsDecoder();

                    // // Decode total actions
                    // if (actionDecoder.TryDecode<TwinActions>(py.total.AsPyObject(), out var totalActions))
                    //     results.Total = totalActions;

                    // // Decode total nodes results
                    // if (nodesResultsDecoder.TryDecode<TwinNodesResults>(py.total_nodes.AsPyObject(), out var totalNodesResults))
                    //     results.TotalNodes = totalNodesResults;

                    // // Decode total elements results
                    // if (elementsResultsDecoder.TryDecode<TwinElementsResults>(py.total_elements.AsPyObject(), out var totalElementsResults))
                    //     results.TotalElements = totalElementsResults;

                    value = (T)(object)results;
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
