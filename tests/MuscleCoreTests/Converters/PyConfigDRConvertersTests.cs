using MuscleCore.Converters;
using MuscleCore.Solvers;
using Microsoft.VisualStudio.TestTools.UnitTesting;
using Python.Runtime;
using System.IO;
using MuscleCore.PythonNETInit;

namespace MuscleCoreTests.Converters
{
    [TestClass]
    public class PyConfigDRConvertersTests
    {
        private static string condaEnvPath;
        private static string pythonDllName;
        private static string srcDir;
        private CoreConfigDR _testConfig;
        private PyConfigDREncoder _encoder;

        [ClassInitialize]
        public static void ClassInitialize(TestContext testContext)
        {
            condaEnvPath = PythonNETConfig.condaEnvPath;
            pythonDllName = PythonNETConfig.pythonDllName;

            srcDir = Path.GetFullPath(Path.Combine(
            Directory.GetCurrentDirectory(), "..", "..", "..", "..", "..", "src"));

            PythonNETManager.Initialize(condaEnvPath, pythonDllName, srcDir);
        }

        [ClassCleanup]
        public static void ClassCleanup()
        {
            PythonNETManager.ShutDown();
        }

        [TestInitialize]
        public void SetUp()
        {
            // Create a test configuration with non-default values
            _testConfig = new CoreConfigDR(
                dt: 0.02,
                massAmplFactor: 2.0,
                minMass: 0.01,
                maxTimeStep: 5000,
                maxKEResets: 500,
                zeroResidualRTol: 1e-5,
                zeroResidualATol: 1e-7
            );
            
            _encoder = new PyConfigDREncoder();
        }

        [TestMethod]
        public void Test_Encoder_CanEncode()
        {
            // Should encode CoreConfigDR
            Assert.IsTrue(_encoder.CanEncode(typeof(CoreConfigDR)));

            // Should not encode other types
            Assert.IsFalse(_encoder.CanEncode(typeof(string)));
            Assert.IsFalse(_encoder.CanEncode(typeof(int)));
            Assert.IsFalse(_encoder.CanEncode(typeof(object)));
        }

        [TestMethod]
        public void Test_Encoder_TryEncode()
        {
            using (Py.GIL())
            {
                // Should successfully encode CoreConfigDR
                var pyConfig = _encoder.TryEncode(_testConfig);
                Assert.IsNotNull(pyConfig);

                // Should return null for non-CoreConfigDR objects
                Assert.IsNull(_encoder.TryEncode("not a config"));
                Assert.IsNull(_encoder.TryEncode(42));
                Assert.IsNull(_encoder.TryEncode(new object()));
            }
        }
    }
}
