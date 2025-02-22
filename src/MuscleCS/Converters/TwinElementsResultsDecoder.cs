using MuscleCore.TwinModel;
using Python.Runtime;
using System.Runtime.InteropServices;

namespace MuscleCore.Converters
{
    public class TwinElementsResultsDecoder : IPyObjectDecoder
    {
        public bool CanDecode(PyType objectType, Type targetType)
        {
            if (targetType != typeof(TwinElementsResults))
                return false;

            using (Py.GIL())
            {
                try
                {
                    return objectType.Name == "Twin_ElementsResults";
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
            if (typeof(T) != typeof(TwinElementsResults))
                return false;

            using (Py.GIL())
            {
                try
                {
                    dynamic py = pyObj.As<dynamic>();
                    
                    var tension = ((PyObject)py.tension).As<double[]>();
                    var elasticElongation = ((PyObject)py.elastic_elongation).As<double[]>();

                    value = (T)(object)new TwinElementsResults 
                    { 
                        Tension = tension,
                        ElasticElongation = elasticElongation
                    };
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
