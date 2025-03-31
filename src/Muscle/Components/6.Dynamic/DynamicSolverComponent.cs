using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Grasshopper.Kernel.Parameters;
using Rhino.Geometry;
using System.IO;
using MuscleApp.ViewModel;
using MuscleApp.Solvers;
using Muscle.View;
using Muscle.Converters;
using MuscleCore.PythonNETInit;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Dynamic
{
    public class DynamicSolverComponent : GH_Component
    {
        public static readonly string[] _massMatrixOptions= {"0. Neglect element masses", "1. Lumped Mass Matrix", "2. Consistent Mass Matrix"};
        public static readonly int[] _optionsIdx = {0, 1, 2};

        public DynamicSolverComponent()
          : base("Dynamic Modal Analysis", "Dynamic",
                "Compute the natural vibration modes of the structure and their frequencies. This component solves the eigenvalue problem with the mass matrix and the tangent stiffness matrix (= material + geometric stiffnesses in the current state).",
              GHAssemblyName, Folder6_Dynamic)
        {
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //return Properties.Resources.Lumped;
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("7d6853e4-ea1b-43e6-b66e-9ef122987812"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may preloaded or self-stressed from previous calculations. The tangent stiffness matrix will be computed in the current structure's state.", GH_ParamAccess.item);
            pManager.AddGenericParameter("Point Mass", "point m (kg)", "List of point masses [kg] added up on the diagonal of the mass matrix (shape (3n,3n), n being the number of nodes, 3 being the X, Y, Z directions).", GH_ParamAccess.tree);
            pManager.AddNumberParameter("Element Mass", "elem m (kg)", "List of element masses [kg]. If null input, the element's masses are automatically computed from their free length, cross-sectional area and material specific mass.", GH_ParamAccess.tree);
            pManager.AddIntegerParameter("Element Mass Matrix", "elem Matrix (-)", "The lumped mass option computes a diagonal matrix (as above point masses) where half of the element mass is added up to each of both end nodes. \nLast option computes the so-called consistent mass matrix which is not diagonal.", GH_ParamAccess.item,0);
            pManager.AddIntegerParameter("nModes", "nModes", "Number of natural modes to compute. nModes=0 will compute all the natural modes.", GH_ParamAccess.item,0);
            pManager[1].Optional = true;
            pManager[2].Optional = true;
            pManager[3].Optional = true;
            pManager[4].Optional = true;
            
            // create a dropdown list for the user to select a supported element mass matrix option
            var option = pManager[3] as Param_Integer;
            for (int i = 0; i < _massMatrixOptions.Length; i++)
            {
                string optionName = _massMatrixOptions[i];
                int optionIdx = _optionsIdx[i];
                option.AddNamedValue(optionName, optionIdx);
            }
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "Unchanged structure", GH_ParamAccess.item);
            pManager.AddNumberParameter("Natural Frequencies", "freq", "Natural frequencies (Hz) associated with the natural modes", GH_ParamAccess.list);
            pManager.AddVectorParameter("Natural Modes", "modes", "Natural mode shapes (-) of vibration computed from the mass and tangent stiffness matrices", GH_ParamAccess.tree);
            pManager.AddVectorParameter("Point Mass", "point m (kg)", "Total point masses [kg] resulting from the addition of the input Point Masses and Element Masses. \nNo difference can be seen here between the lumped mass and the constistent mass options, but a different mass matrix (diagonal or not) was well used for the dynamic modal analysis.", GH_ParamAccess.list);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // Check if Python.NET is initialized
            if (!PythonNETManager.IsInitialized)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }

            // 1) Collect Data
            GH_Truss gh_truss = new GH_Truss();
            GH_Structure<IGH_Goo> gh_pointMass = new GH_Structure<IGH_Goo>();
            GH_Structure<GH_Number> gh_elemMass = new GH_Structure<GH_Number>();
            int massMatrixOption = 0;
            int nModes = 0;

            if (!DA.GetData(0, ref gh_truss)) { return; }
            if (!DA.GetDataTree(1, out gh_pointMass)) { }
            if (!DA.GetDataTree(2, out gh_elemMass)) { }
            if (!DA.GetData(3, ref massMatrixOption)) { }
            if (!DA.GetData(4, ref nModes)) { }

            // 2) Transform data before solving 
            Truss truss = gh_truss.Value;
            
            // Extract point and element masses from the data tree
            List<PointMass> pointMasses = GH_Decoders.ToPointMassList(gh_pointMass);
            List<double> elementMasses = GH_Decoders.ToDoubleList(gh_elemMass);


            // 3) Solve using the DynamicModalAnalysis solver
            ResultsDynamic resultsDynamic = null;
            try
            {
                resultsDynamic = DynamicModalAnalysis.Solve(truss, pointMasses, elementMasses, massMatrixOption, nModes);
            }
            catch (Exception e)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Failed to solve the dynamic modal analysis: {e.Message}");
                return;
            }

            // 4) Check if the solution was successful
            if (resultsDynamic == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to solve the dynamic modal analysis.");
                return;
            }

            // 5) Set outputs
            DA.SetData(0, gh_truss);
            DA.SetDataList(2, GH_Encoders.ToBranch(resultsDynamic.Frequencies));
            DA.SetDataTree(1, GH_Encoders.ToTree(resultsDynamic.ModeShapes));
            DA.SetDataList(3, GH_Encoders.ToBranch(resultsDynamic.Masses));
        }
    }
}
