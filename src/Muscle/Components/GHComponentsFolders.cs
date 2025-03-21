using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Grasshopper.Kernel;

namespace Muscle.Components
{
    public static class GHComponentsFolders
    {

        private static MuscleInfo info = new MuscleInfo();

        public static string GHAssemblyName // "Muscle"
        {
            get
            {
                return info.Name; 
            }
        }
        public static string Folder0_PythonInit { get { return "0.Initialize Python"; } }
        public static string Folder1_Param { get { return "1.Parameters"; } }
        public static string Folder2_ConstructFEM { get { return "2.Construct FEModel"; } }
        public static string Folder3_StaticLoading { get { return "3.Static Loading"; } }
        public static string Folder4_StaticSolvers { get { return "4.Static Solvers"; } }
        public static string Folder5_DeconstructFEM { get { return "5.Deconstruct FEModel"; } }
        public static string Folder6_Dynamic { get { return "6.Dynamic Modal Analysis"; } }
        public static string Folder7_Display { get { return "7.Display"; } } 
        public static string Folder8_Util { get { return "8.Utilities"; } } 

    }
}