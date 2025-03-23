using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;
using MuscleApp.Solvers;
using Muscle.View;
using Muscle.Converters;
using MuscleCore.PythonNETInit;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.StaticLoading
{
    /// <summary>
    /// Component to localize self-stress modes of a structure using a recursive reduction algorithm.
    /// </summary>
    public class LocalizeSelfStressModesComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the LocalizeSelfStressModesComponent class.
        /// </summary>
        public LocalizeSelfStressModesComponent()
          : base("Localize Self-Stress Modes", "Localize",
                "(Work in progress) Try to localize the self-stress modes of the structure using a recursive reduction algorithm. Reference: Sánchez R., Maurin B., Kazi-Aoual M. N., and Motro R., Selfstress States Identification and Localization in Modular Tensegrity Grids, Int. J. Sp. Struct., vol. 22, no. 4, pp. 215–224, Nov. 2007.",
              GHAssemblyName, Folder3_StaticLoading)
        {
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
            get { return new Guid("1a42d0b0-af1f-4654-8a01-f8f1e3f3b690"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "Structure to localize self-stress modes.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Self-Stress Modes", "Vs_T", "Self-stress modes of the structure (_T = Transpose, i.e. input modes as row vectors)", GH_ParamAccess.tree);
            pManager.AddNumberParameter("Absolute tolerance", "atol", "Tolerance under which a force (N) is considered as 0 in the mode.", GH_ParamAccess.item, 1e-10);
            pManager[2].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "Unchanged structure.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Localised Self-Stress Modes", "S_T", "Localised self-stress modes of the structure (_T = Transpose, i.e. modes are stored as row vectors)", GH_ParamAccess.tree);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            if (!PythonNETManager.IsInitialized)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }

            // 1) Collect Inputs
            GH_Truss gh_struct = new GH_Truss();
            GH_Structure<GH_Number> gh_Vs_T = new GH_Structure<GH_Number>();
            double aTol = 1e-10;

            if (!DA.GetData(0, ref gh_struct)) { return; }
            if (!DA.GetDataTree(1, out gh_Vs_T)) { return; }
            if (!DA.GetData(2, ref aTol)) { }

            Truss structure = gh_struct.Value;
            
            // Convert the GH_Structure to a 2D array for Python
            double[,] Vs_T = GH_Decoders.To2dArray(gh_Vs_T);
            
            // Check if we have any self-stress modes
            if (Vs_T.GetLength(0) == 0)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "No self-stress modes provided.");
                DA.SetData(0, gh_struct);
                return;
            }
            
            // 2) Call the Python function to localize the self-stress modes
            double[,] localModes = null;
            
            try
            {
                localModes = SelfStressModes.Localize(structure, Vs_T, aTol);
            }
            catch (Exception ex)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Error: {ex.Message}");
                return;
            }
            // 4) Check if the solution was successful
            if (localModes == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to localize the self-stress modes.");
                return;
            }
            
            // 4) Set outputs
            DA.SetData(0, gh_struct);
            DA.SetDataTree(1, GH_Encoders.ToTree(localModes));
        }
    }
}
