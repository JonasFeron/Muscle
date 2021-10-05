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
    }
}
