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
    public class DynamicSolverComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DynamicSolverComponent()
          : base("Dynamic Solver TEST", "DSTEST",
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
            get { return new Guid("14e22534-7087-42cf-8de2-1d9044065502"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may already be subjected to some loads or prestress from previous calculations.", GH_ParamAccess.item);
            pManager.AddGenericParameter("Point Mass (kg)", "Point Mass (kg)", "The mass who is considered at each node for the dynamic computation. 1 [kg] is considered for all nodes if no input is given or if less/more than the number of nodes. All values will be used as absolute values.", GH_ParamAccess.tree);
            pManager.AddIntegerParameter("Number of frequencies wanted", "Num. freq. wanted", "To define the number of frequencies and modes that need to be computed. For the value 0, all the frequencies will be computed.", GH_ParamAccess.item);


        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure containing the total results.", GH_ParamAccess.item);

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
            List<double> DynMassIN = new List<double>(); // Default value
            int MaxFreqWtd = 0;
            GH_Structure<IGH_Goo> gh_mass = new GH_Structure<IGH_Goo>();
            //Obtain the data if the component is connected
            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetDataTree(1, out gh_mass)) { }
            if (!DA.GetData(2, ref MaxFreqWtd)) { } //Number of frequencies /mode that the user want to display


            //2) Format data before sending and solving in python
            StructureObj new_structure = structure.Duplicate(); //a) Duplicate the structure. The elements still contains the Initial Tension forces. The nodes are in their previously equilibrated coordinates with previous load already applied on it.

            //Create a list with a length = Number of nodes
            for (int i = 0; i < structure.NodesCount; i++)
            {
                DynMassIN.Add(0.0);
            }

            structure.DynMass = DynMassIN;
            //Save the data of dynamic masses in the Structure
            bool success1 = RegisterPointMass(structure, gh_mass.FlattenData()); // structure.DynMass was filled with the loads



            //3) Solve in python
            if (AccessToAll.pythonManager == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Please restart the \"Initialize Python\" Component.");
                DA.SetData(0, null);
                return;
            }

            SharedData data = new SharedData(structure, DynMassIN, MaxFreqWtd); //Object data contains all the essential informations of structure + the dynMass considered
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

            new_structure.PopulateWithSolverResult_dyn(result);

            List<Vector3d> ModeUsedVector = new List<Vector3d>(); //Create the list of mode with a vector shape (dx,dy,dz) with a length equal to the number of nodes.
            int NumberOfNodes = structure.NodesCount;
            List<List<Vector3d>> ModeVect_construction = new List<List<Vector3d>>();
            for (int i = 0; i < new_structure.NumberOfFrequency; i++)
            {
                List<Vector3d> ModeIteration3D = new List<Vector3d>();
                for (int j = 0; j < NumberOfNodes; j++)
                {
                    Vector3d ToAdd = new Vector3d();
                    ToAdd.X = new_structure.Mode[i][j * 3];
                    ToAdd.Y = new_structure.Mode[i][j * 3 + 1];
                    ToAdd.Z = new_structure.Mode[i][j * 3 + 2];
                    ModeIteration3D.Add(ToAdd);
                }
                ModeVect_construction.Add(ModeIteration3D);
            }
            new_structure.ModeVector = ModeVect_construction;



            //Not need to create a new structure because the computation is not changing the structure
            //Obtain the results from "result"
            GH_StructureObj gh_structure = new GH_StructureObj(new_structure);
            DA.SetData(0, gh_structure);

        



            log.Info("Dynamic computation: END SOLVE INSTANCE");

            
        }
        private bool RegisterPointMass(StructureObj structure, List<IGH_Goo> datas)
        {
            //return true if at least one load is added on the structure
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            //new_structure.LoadsToApply = new List<Vector3d>(); //this is already done in Duplicate
            //foreach (var node in new_structure.StructuralNodes) new_structure.LoadsToApply.Add(new Vector3d(0.0, 0.0, 0.0)); // initialize the LoadsToApply vector with 0 load for each DOF. 


            

            
            
            PointLoad load;
            foreach (var data in datas) //Go trough the data
            {
                if (data is GH_PointLoad)
                {
                    load = ((GH_PointLoad)data).Value; //retrieve the pointload inputted by the user
                    int Index = load.NodeInd;
                    // we need to know on which point or node the load will have to be applied
                    int ind = -1;
                    if ((load.NodeInd != -1) || (load.NodeInd <= structure.NodesCount)) //PointsLoad can be defined on a point or on a node index
                    {
                        ind = load.NodeInd;
                        structure.DynMass[ind] += load.Vector.Z; //If Point mass is applied on a node of the str
                    }
                    success = true;
                }
            }

            return success;
        }
    }
}
