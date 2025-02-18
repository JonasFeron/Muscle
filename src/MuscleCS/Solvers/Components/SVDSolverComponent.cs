using System;
using System.IO;
using Grasshopper.Kernel;
using Muscle.PythonLink;
using Muscle.Structure;
using Newtonsoft.Json;
using Muscle.Util;
using Muscle.PythonNETComponents.TwinObjects;
using Python.Runtime;

namespace Muscle.Solvers
{
    public class SVDSolverComponent : GH_Component
    {
        private SharedData prev_data;
        private SharedAssemblyResult prev_result;

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public SVDSolverComponent()
          : base("Solver - Selfstress and mechanisms analysis - by Singular Value Decomposition", "SVD",
                "Find the self-stress modes and mechanisms of the structure.\n" +
                "ref: S. Pellegrino, Structural computations with the singular value decomposition of the equilibrium matrix, Int.J. Sol. and Struct.,30(21),1993,p3025-3035",
              "Muscles", "Solvers")
        {
            prev_data = null;
            prev_result = null;
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("016c793a-aa02-416c-9bcf-4d06d43c1b01"); }

        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may already be subjected to some loads or prestress from previous calculations.", GH_ParamAccess.item);
            pManager.AddNumberParameter("ZeroTol", "Tol", "Tolerance factor underwhich a singular value of the equilibrium matrix is considered as 0. \nIn particular, a singular value Lambda is considered =0 if Lambda < LambdaMAX * Tol ", GH_ParamAccess.item,0.001);
            pManager[1].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "Unchanged structure.", GH_ParamAccess.item);//0
            pManager.AddIntegerParameter("Rank", "r", "Rank of equilibrium matrix", GH_ParamAccess.item); //1
            pManager.AddNumberParameter("S", "S", "Eigen values of equilibrium matrix", GH_ParamAccess.list); //2
            pManager.AddNumberParameter("A", "A", "Equilibrium matrix", GH_ParamAccess.tree); //3
            pManager.AddIntegerParameter("StaticDeg", "s", "Degree of static indeterminacy", GH_ParamAccess.item); //4
            pManager.AddNumberParameter("Self-Stress", "SS", "Self-stress modes of the structure", GH_ParamAccess.tree); //5
            pManager.AddIntegerParameter("KinematicDeg", "m", "Degree of kinematic indeterminacy, or i.e. number of mechanisms (infinitesimal and rigid body)", GH_ParamAccess.item); //6
            pManager.AddNumberParameter("Mechanisms", "Um", "Mechanisms of the structure", GH_ParamAccess.tree); //7
            pManager.AddNumberParameter("SS Stiffness", "Ks", "[kN/m] Stiffness of self-stress modes", GH_ParamAccess.tree); //8
            pManager.AddNumberParameter("SM Prestress level", "SMa", "[kN/m] Sensitivity Matrix of the prestress levels (=Ks*SS) to 1m imposed elongations in the elements", GH_ParamAccess.tree); //9
            pManager.AddNumberParameter("SM displacements", "SMd", "[m/m] Sensitivity Matrix of the displacements to 1m imposed elongations in the elements", GH_ParamAccess.tree); //9



        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string pythonScript = "MainAssembleStructure"; // ensure that the python script is located in AccessToAll.pythonProjectDirectory, or provide the relative path to the script.
            if (!AccessToAll.hasPythonStarted)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }
            if (!File.Exists(Path.Combine(AccessToAll.pythonProjectDirectory, pythonScript + ".py")))
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Please ensure that \"{pythonScript}\" is located in: {AccessToAll.pythonProjectDirectory}");
                return;
            }

            // 1) Collect Inputs
            //bool dataHasChanged = true;
            GH_StructureObj gh_struct = new GH_StructureObj();
            double ZeroTol = -1;


            if (!DA.GetData(0, ref gh_struct)) { return; }
            if (!DA.GetData(1, ref ZeroTol)) { }


            StructureObj structure = gh_struct.Value;
            structure.Residual0Threshold = ZeroTol;
            // 2) Create and solve geometry object 

            SharedAssemblyResult result = new SharedAssemblyResult();
            SharedData data = new SharedData(structure); //Object data contains all the essential informations of structure
            string jsonData = JsonConvert.SerializeObject(data, Formatting.None);
            dynamic jsonResult = null;

            //2) Solve in python
            var m_threadState = PythonEngine.BeginAllowThreads();

            using (Py.GIL())
            {
                try
                {
                    dynamic script = PyModule.Import(pythonScript);
                    dynamic mainFunction = script.main;
                    jsonResult = mainFunction(jsonData);
                    JsonConvert.PopulateObject((string)jsonResult, result);
                }
                catch (PythonException ex)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, ex.Message);
                }
                catch (Exception e)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"python result= {jsonResult}");
                    return;
                }
            }

            PythonEngine.EndAllowThreads(m_threadState);


            // 3) Set outputs
            DA.SetData(0, gh_struct);
            DA.SetData(1, result.r);
            DA.SetDataList(2, result.S);
            DA.SetDataTree(3, result.ListListToGH_Struct(result.A));
            DA.SetData(4, result.s);
            DA.SetDataTree(5, result.ListListToGH_Struct(result.SS));
            DA.SetData(6, result.m);
            DA.SetDataTree(7, result.ListListToGH_Struct(result.Um_row));
            DA.SetDataTree(8, result.ListListToGH_Struct(Util.Util.MultiplyListListPerX(result.Ks,0.001)));
            DA.SetDataTree(9, result.ListListToGH_Struct(Util.Util.MultiplyListListPerX(result.Sa,0.001)));
            DA.SetDataTree(10, result.ListListToGH_Struct(result.Sd));
        }

    }
}
