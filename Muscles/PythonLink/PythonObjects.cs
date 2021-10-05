using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;

namespace Muscles.PythonLink
{
    public class PythonCommand
    {
        public Guid Id { get; }
        public string PythonFileName { get; }
        public List<string> Parameters { get; }
        public PythonCommand(string pythonFileName, params string[] args)
        {
            Id = Guid.NewGuid();
            PythonFileName = pythonFileName;
            Parameters = args.Select(o => $"{o}").ToList();
        }

        /// <summary>
        /// Write all the data required to execute a PythonCommand in a file.txt and return the path to this file. 
        /// </summary>
        /// <param name="command"></param>
        /// <returns></returns>
        public string WriteDataInTxtFile()
        {
            string file = null;
            if (PythonFileName == AccessToAll.Main_Test) file = AccessToAll.File_Test_Data;
            else if (PythonFileName == AccessToAll.Main_Assemble) file = AccessToAll.File_Assemble_Data;
            else if (PythonFileName == AccessToAll.Main_LinearSolve) file = AccessToAll.File_LinearSolve_Data;
            else if (PythonFileName == AccessToAll.Main_NonLinearSolve) file = AccessToAll.File_NonLinearSolve_Data;
            else file = "error_Data.txt";

            string IOPath = Path.Combine(AccessToAll.Main_Folder, "IO");
            DirectoryInfo IO = Directory.CreateDirectory(IOPath);
            string txtFilePath = Path.Combine(IO.FullName,file); // for instance: "...\Muscles\IO\Assemble_Data.txt"

            using (StreamWriter outputFile = new StreamWriter(txtFilePath, false))
            {
                outputFile.WriteLine(Id);
                //outputFile.WriteLine($"{Parameters.Aggregate((o, p) => $"{o} {p}")}");
                foreach (string param in Parameters)
                {
                    outputFile.WriteLine(param);
                }
                outputFile.Close();
            }
            return ToStringRepr(txtFilePath);
        }

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

    public class PythonResult
    {
        public Guid Id { get; }
        public string Result { get; }

        public PythonResult(Guid id, string result)
        {
            Id = id;
            Result = result;
        }


    }
}
