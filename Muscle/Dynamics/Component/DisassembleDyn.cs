using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.Elements;
using Muscle.Loads;
using Muscle.Nodes;
using Muscle.PythonLink;
using Muscle.Dynamics;
using Muscle.PythonLink.Component;
using Muscle.Structure;
using Newtonsoft.Json;
using Rhino.Geometry;

namespace Muscle.Dynamics
{
    public class DisassembleDyn : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DisassembleDyn()
          : base("Disassemble Dynamic", "DS","Give the dynamic parameter and result of the dynamic computation who is stored in the structure.",
              "Muscles", "Dynamics")
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
            get { return new Guid("bbdbc522-837b-4e79-8b75-6d7cf8651c4f"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may already be subjected to some loads or prestress from previous calculations.", GH_ParamAccess.item);

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddNumberParameter("Nodal masses", "Mass (kg/node)", "The mass who is considered at each node for the dynamic computation.", GH_ParamAccess.list); 
            pManager.AddIntegerParameter("Number of frequency(ies) computed", "Num. of freq. computed", "Number of natural frequencies of the structure. It is equal to the number of DOF of the structure.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Total number of frequencies", "Tot. Num. freq.", "Total number of the frequencies that the structure has.", GH_ParamAccess.item);
            pManager.AddGenericParameter("Frequency(ies)", "Freq. (Hz)", "Natural frequencies of the structure ranked from the smallest to the biggest.", GH_ParamAccess.list);
            pManager.AddGenericParameter("Mode(s)", "Mode(s)", "Modes of the structure ranked as the returned frequencies.(containing also the zero displacement is blocked directions.)", GH_ParamAccess.list);
            //pManager.AddGenericParameter("Structure", "struct", "A structure containing the total results.", GH_ParamAccess.item);
            

            //AddNumberParameter
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            log.Info("Dynamic computation: NEW SOLVE INSTANCE");
            //1) Collect Data
            StructureObj structure = new StructureObj();

            //Obtain the data if the component is connected
            if (!DA.GetData(0, ref structure)) { return; }


            //Return the infos

            DA.SetDataList(0, structure.DynMass);
            DA.SetData(1, structure.NumberOfFrequency);
            DA.SetData(2, structure.DOFfreeCount);
            DA.SetDataList(3, structure.Frequency); //Don't use PopulateWithSolverResult
            //DA.SetDataTree(4, structure.ListListToGH_Struct(structure.Mode));//result.ListListToGH_Struct(result.Modes)
            DA.SetDataTree(4, structure.ListListVectToGH_Struct(structure.ModeVector));//result.ListListToGH_Struct(result.Modes)
            //DA.SetData(0, new_structure.NumberOfFrequency);
            //DA.SetDataList(1, new_structure.Frequency); //Don't use PopulateWithSolverResult
            //DA.SetData(2, new_structure.Mode);
            //DA.SetDataTree(2, result.ListListToGH_Struct(result.Modes)); //Need to use this to be able to 
            // Before it was SetData


            log.Info("Dynamic computation: END SOLVE INSTANCE");
        }

    }
}
