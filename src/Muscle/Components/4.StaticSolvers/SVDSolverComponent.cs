using System;
using System.IO;
using Grasshopper.Kernel;

using Muscle.Util;
using Python.Runtime;
using MuscleApp.ViewModel;
using Muscle.View;
using static Muscle.Converters.GH_Encoders;
// using MuscleApp.Solvers;
// using MuscleCore.Solvers;


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
            pManager.AddGenericParameter("Structure", "struct", "A structure which may be prestressed (preloaded or self-stressed) from previous calculations.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Relative tolerance", "rtol", "Tolerance factor underwhich a singular value of the equilibrium matrix is considered as 0. \nIn particular, a singular value Lambda is considered =0 if Lambda < LambdaMAX * rTol ", GH_ParamAccess.item,0.001);
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
            pManager.AddIntegerParameter("StaticDeg", "s", "Degree of static indeterminacy", GH_ParamAccess.item); //3
            pManager.AddNumberParameter("Self-Stress", "Vs_T", "Self-stress modes of the structure", GH_ParamAccess.tree); //4
            pManager.AddNumberParameter("Extensional Modes", "Vr_T", "Extensional modes of the structure", GH_ParamAccess.tree); //5
            pManager.AddIntegerParameter("KinematicDeg", "m", "Degree of kinematic indeterminacy.", GH_ParamAccess.item); //6
            pManager.AddNumberParameter("Mechanisms", "Um_T", "Mechanisms of the structure, in the form of row vectors.", GH_ParamAccess.tree); //7
            pManager.AddNumberParameter("Extensional Modes", "Ur_T", "Extensional modes of the structure, in the form of row vectors.", GH_ParamAccess.tree); //8
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            if (!AccessToAll.hasPythonStarted)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }

            // 1) Collect Inputs
            //bool dataHasChanged = true;
            GH_StructureState gh_struct = new GH_StructureState();
            double rTol = -1;


            if (!DA.GetData(0, ref gh_struct)) { return; }
            if (!DA.GetData(1, ref rTol)) { }

            StructureState structure = gh_struct.Value;
            var svdResult = MuscleApp.Solvers.SVD.Solve(structure, rTol);

            // 3) Set outputs
            DA.SetData(0, gh_struct);
            DA.SetData(1, svdResult.r);
            DA.SetDataList(2, ToBranch(svdResult.S));
            DA.SetData(3, svdResult.s);
            DA.SetDataTree(4, ToTree(svdResult.Vs_T));
            DA.SetDataTree(5, ToTree(svdResult.Vr_T));
            DA.SetData(6, svdResult.m);
            DA.SetDataTree(7, ToTree(svdResult.Ur_T));
            DA.SetDataTree(8, ToTree(svdResult.Um_T));

        }

    }
}
