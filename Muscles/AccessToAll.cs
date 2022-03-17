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
        public static double DisplaySupportAmpli = 1.0; 
        //public static List<double> DisplaySupportAmpli = new List<double>() {1.0};//default value  
        public static double DisplayLoadAmpli = 1.0; //default value
        public static int DisplayDecimals = 1;

        public static PythonManager pythonManager = null; //pythonManager of the current Canvas
        public static bool user_mode = true;
        public static string Main_Folder = @"C:\Users\desme\Documents\GitHub\Muscles_ADE";
        public static string assemblyTitle = "Muscles v0.5";

        public static string MainTest
        {
            get
            {
                if (user_mode == true) return "DoStuffInPython.pyc";
                else return "DoStuffInPython.py";
            }
        }
        public static string MainAssemble
        {
            get
            {
                if (user_mode == true) return "MainAssembleStructure.pyc";
                else return "MainAssembleStructure.py";
            }
        }
        public static string MainLinearSolve
        {
            get
            {
                if (user_mode == true) return "MainLinearSolveStructure.pyc";
                else return "MainLinearSolveStructure.py";
            }
        }
        public static string MainNonLinearSolve
        {
            get
            {
                if (user_mode == true) return "MainNonLinearSolveStructure.pyc";
                else return "MainNonLinearSolveStructure.py";
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
        public static string Dyn
        {
            get
            {
                if (user_mode == true) return "ModuleDynamics.pyc";
                else return "ModuleDynamics.py";
            }
        }

        public const string FileTestData = "TestData.txt";
        //public const string File_Test_Result = "Test_Result.txt"; //defined in python
        public const string FileAssembleData = "AssembleData.txt";
        //public const string File_Assemble_Result = "AssembleResult.txt";
        public const string FileLinearSolveData = "LinearSolveData.txt";
        //public const string File_LinearSolve_Result = "LinearSolveResult.txt";
        public const string FileNonLinearSolveData = "NonLinearSolveData.txt";
        //public const string File_NonLinearSolve_Result = "NonLinearSolveResult.txt";
        public const string FileDRSolveData = "DynamicRelaxationData.txt";



        public static Vector3d g = new Vector3d(0, 0, -9.81);


        #endregion Properties

    }
}
