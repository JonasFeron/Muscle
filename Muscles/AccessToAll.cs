using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Muscles.PythonLink;
using Rhino.Geometry;

namespace Muscles
{
    /// <summary>
    /// A Class containing Properties and Methods accessible to All components
    /// </summary>
    public static class AccessToAll
    {


        #region Properties
        public static double DisplaySupportAmpli = 1.0; //N.B. double are value type which means its value is given once for all.to change value dynamically, use reference type such as list
        //public static List<double> DisplaySupportAmpli = new List<double>() {1.0};//default value  
        public static double DisplayLoadAmpli = 1.0; //default value
        public static int DisplayDecimals = 1;

        public static PythonManager pythonManager = null; //pythonManager of the current Canvas
        public static bool user_mode = true;
        public static string Main_Folder = @"C:\Users\Jferon\OneDrive - UCL\Doctorat\recherche\code\5 - logiciel CS\Muscles";
        public static string Main_Test
        {
            get
            {
                if (user_mode == true) return "DoStuffInPython.pyc";
                else return "DoStuffInPython.py";
            }
        }
        public static string Main_Assemble
        {
            get
            {
                if (user_mode == true) return "Main_AssembleStructure.pyc";
                else return "Main_AssembleStructure.py";
            }
        }
        public static string Main_LinearSolve
        {
            get
            {
                if (user_mode == true) return "Main_LinearSolveStructure.pyc";
                else return "Main_LinearSolveStructure.py";
            }
        }
        public static string Main_NonLinearSolve
        {
            get
            {
                if (user_mode == true) return "Main_NonLinearSolveStructure.pyc";
                else return "Main_NonLinearSolveStructure.py";
            }
        }
        public static string MainDRSolve
        {
            get
            {
                if (user_mode == true) return "MainDynamicRelaxation.pyc";
                else return "MainDynamicRelaxation.py";
            }
        }

        public const string File_Test_Data = "Test_Data.txt";
        //public const string File_Test_Result = "Test_Result.txt"; //defined in python
        public const string File_Assemble_Data = "Assemble_Data.txt";
        //public const string File_Assemble_Result = "Assemble_Result.txt";
        public const string File_LinearSolve_Data = "LinearSolve_Data.txt";
        //public const string File_LinearSolve_Result = "LinearSolve_Result.txt";
        public const string File_NonLinearSolve_Data = "NonLinearSolve_Data.txt";
        //public const string File_NonLinearSolve_Result = "NonLinearSolve_Result.txt";
        public const string File_DRSolve_Data = "DynamicRelaxationData.txt";



        public static Vector3d g = new Vector3d(0, 0, -9.81);


        #endregion Properties

    }
}
