using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles.Util
{
    /// <summary>
    /// Contains a bunch of usefull method
    /// </summary>
    public static class Util
    {
        /// <summary>
        /// Returns the representation of a string considering special characters. 
        /// 
        /// "Hello World" -> "\"Hello World\"" 
        /// </summary>
        /// <param name="data"></param>
        public static string ToStringRepr(string data)
        {
            StringBuilder result = new StringBuilder();

            result.Append("\"");
            foreach (char c in data)
            {
                if (c.ToString() == "\"") result.Append("\\\"");
                else result.Append(c);
            }
            result.Append("\"");
            return result.ToString();
        }
        public static List<List<double>> MultiplyListListPerX(List<List<double>> datalistlist, double X)
        {
            List<List<double>> res = new List<List<double>>();
            List<double> list = null;

            foreach (List<double> datalist in datalistlist)
            {
                list = new List<double>();
                foreach(double data in datalist)
                {
                    list.Add(data * X);
                }
                res.Add(list);
            }
            return res;
        }
    }
}
