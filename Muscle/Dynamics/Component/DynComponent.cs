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
    public class DynComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DynComponent()
          : base("Dynamic Solver", "DS",
                "Compute the frequency(ies) and the mode(s) of the struture having a certain mass on each node. The computation is done on the state of the structure. It includes the influence of Lfree (pretension) and the possible applied load.",
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
            get { return new Guid("a1687993-3c2e-471a-809b-cc27b5ff8679"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may already be subjected to some loads or prestress from previous calculations.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Mass", "Mass (kg)", "The mass who is considered at each node for the dynamic computation.", GH_ParamAccess.item);

            //pManager[1].Optional = true; /A mettre ? 
            //pManager[2].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddIntegerParameter("Number of frequency(ies)", "#freq", "", GH_ParamAccess.item);
            pManager.AddGenericParameter("Frequency(ies)", "Freq. (Hz)", "All natural frequencies of the structure ranked from the smallest to the biggest.", GH_ParamAccess.list);
            pManager.AddGenericParameter("Mode", "Mode", "All modes of the structure ranked as the returned frequencies.", GH_ParamAccess.list);
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
            double DynMass = 1; // Default value

            //Obtain the data if the component is connected
            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetData(1, ref DynMass)) { } ///problemn


            //2) Format data before sending and solving in python
            //StructureObj new_structure = structure.Duplicate(); //a) Duplicate the structure. The elements still contains the Initial Tension forces. The nodes are in their previously equilibrated coordinates with previous load already applied on it.


            //bool success1 = RegisterPointLoads(new_structure, gh_loads_ext.FlattenData()); // new_structure.LoadsToApply was filled with the loads
            //bool success2 = RegisterPrestressLoads(new_structure, gh_loads_prestress.FlattenData()); // new_structure.LengtheningsToApply was filled with the length variations

            //new_structure.Residual0Threshold = residual0Threshold;

            /// Call the method "DynMethod" to make the computation in Python
            ///new_structure.DR = new DRMethod(dt, amplMass, minMass, maxTimeStep, maxKEReset);

            //Call the method "DynMethod" to make the computation in Python ?

            // // even if both success 1 and 2 failed to collect data, we can still run the analysis because the LengtheningsToApply can also come from direct change of the Free lengths 
            //if (!success1 && !success2)
            //{
            //    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to collect load data");
            //    return; //abort if both failed
            //} 

            //3) Solve in python
            if (AccessToAll.pythonManager == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Please restart the \"Initialize Python\" Component.");
                DA.SetData(0, null);
                return;
            }

            SharedData data = new SharedData(structure,DynMass) ; //Object data contains all the essential informations of structure + the dynMass considered
            SharedSolverResult result = new SharedSolverResult(); //create the file with the results

            if (AccessToAll.pythonManager != null) // run calculation in python by transfering the data base as a string. 
            {
                log.Debug("pythonManager exists");
                string result_str = null;
                string Data_str = JsonConvert.SerializeObject(data, Formatting.None); /// Json is formatting the data for the transfert to Python
                log.Info("Dynamic computation: ask Python to execute a command");

                result_str = AccessToAll.pythonManager.ExecuteCommand(AccessToAll.DynSolve, Data_str);
                ///AccessToAll launch a Python file who contains the steps of computations

                log.Info("Dynamic computation: received results");
                try
                {
                    JsonConvert.PopulateObject(result_str, result); //Obtain all the results
                }
                catch
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Something went wrong while computing: " + result_str);
                    log.Warn("Dynamic computation: Something went wrong while solving:" + result_str);
                    result = null;
                }
            }

            //Not need to create a new structure because the computation is not changing the structure
            //Obtain the results from "result"
            DA.SetData(0, result.NumberOfFrequency);
            DA.SetDataList(1, result.Frequency); //Don't use PopulateWithSolverResult
            DA.SetDataTree(2, result.ListListToGH_Struct(result.Modes)); //Need to use this to be able to 
            // Before it was SetData


            log.Info("Dynamic computation: END SOLVE INSTANCE");
        }
       
    }
}