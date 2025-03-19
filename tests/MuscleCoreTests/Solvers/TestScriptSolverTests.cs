using Microsoft.VisualStudio.TestTools.UnitTesting;
using System.IO;
using MuscleCore.PythonNETInit;
using MuscleCore.Solvers;

namespace MuscleCoreTests.Solvers
{
    [TestClass]
    public class TestScriptSolverTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;


        [TestInitialize]
        public void Initialize()
        {
            condaEnvPath = PythonNETConfig.condaEnvPath;
            pythonDllName = PythonNETConfig.pythonDllName;

            srcDir = Path.GetFullPath(Path.Combine(
    Directory.GetCurrentDirectory(), "..", "..", "..", "..", "..", "src"));


            PythonNETManager.Initialize(condaEnvPath, pythonDllName, srcDir);
        }

        [TestCleanup]
        public void Cleanup()
        {
            PythonNETManager.ShutDown();
        }



        [TestMethod]
        public void TestHelloFromPython()
        {
            // Arrange
            string str0 = "HELLO";
            string str1 = "from python";

            // Act
            string result = TestScriptSolver.Solve(str0, str1);

            // Assert
            Assert.IsNotNull(result);
            Assert.AreEqual("hello FROM PYTHON", result);
        }
    }
}
