using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using MuscleApp.Solvers;
using MuscleApp.ViewModel;
using Muscle.View;
using Muscle.Converters;
using Rhino.Geometry;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.StaticLoading
{
    /// <summary>
    /// Component to apply a self-stress scenario to a structure based on a branch of tension values.
    /// </summary>
    public class SelfStressScenarioComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the SelfStressScenarioComponent class.
        /// </summary>
        public SelfStressScenarioComponent()
            : base("Self-Stress Scenario", "SelfStress",
                "Compute the free length variations to apply on the elements to achieve the target self-stress state. This component warns if the input axial forces are not in self-equilibrium.",
                GHAssemblyName, Folder3_StaticLoading)
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "Structure to apply self-stress to", GH_ParamAccess.item);
            pManager.AddNumberParameter("Target Tensions", "t (kN)", "Targeted self-stress state (kN) with one axial force value per element", GH_ParamAccess.list);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Prestress", "P", "A Self-stress scenario is a particular prestress scenario where the mechanical devices' length variations compensate the elastic elongations of the elements due to the prestress forces.", GH_ParamAccess.list);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // Input parameters
            GH_Truss ghTruss = null;
            List<double> tensions = new List<double>();

            // Retrieve inputs
            if (!DA.GetData(0, ref ghTruss)) return;
            if (!DA.GetDataList(1, tensions)) return; //kN

            // Get the structure from the GH_Truss wrapper
            Truss structure = ghTruss.Value;
            
            // Apply the self-stress scenario
            List<Prestress> prestressList = SelfStressScenario.ComputeFreeLengthVariation(structure, tensions.Select(t => t * 1000).ToList()); // Convert kN to N
            
            // Check for warnings and display them
            if (structure.warnings.Count > 0)
            {
                foreach (string warning in structure.warnings)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, warning);
                }
                structure.warnings.Clear();
            }
            
            // Set output
            DA.SetDataList(0, GH_Encoders.ToBranch(prestressList));
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                // You can add custom icon here
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("4F5A8B9C-D123-4567-89AB-CDEF01234567"); }
        }
    }
}