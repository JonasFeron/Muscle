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
using Muscle.PythonLink.Component;
using Muscle.Structure;
using Newtonsoft.Json;
using Rhino.Geometry;

namespace Muscle.Solvers
{
    public class DRSolverComponent : GH_Component
    {
        ///private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DRSolverComponent()
          : base("Solver - Non Linear - Dynamic Relaxation Method", "DR",
                "Solve truss with geometric non linearities and large changes of the elements free lengths.",
              "Muscles", "Solvers")
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
            get { return new Guid("5384a9a5-ddf6-44aa-82a9-f848d8440ea8"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may already be subjected to some loads or prestress from previous calculations.", GH_ParamAccess.item);
            pManager.AddGenericParameter("External Point Loads", "Load (kN)", "The additional external point loads to apply on the structure.", GH_ParamAccess.tree);
            pManager.AddGenericParameter("Lengthenings", "Delta L (m)", "The additional length changes to apply on the free lengths of the elements.\n + Lengthening, - Shortening.", GH_ParamAccess.tree);
            pManager.AddNumberParameter("Tolerance 0", "tol (N)", "A structure is in equilibrium if all the unbalanced loads are equal to 0.\n This parameter fixes the ZERO tolerance tol.\n If the norm of the unbalanced loads < tol, the structure is considered in equilibrium.\n The unbalanced load of each node in each direction is equal to the external load applied minus the sum of the internal resisting forces for each element connected to this node.", GH_ParamAccess.item, 0.0001);
            pManager.AddNumberParameter("Delta t", "Dt (s)", "The time increment for the dynamic relaxation analysis", GH_ParamAccess.item, 0.01);
            pManager.AddIntegerParameter("Max Time Step", "max it (/)", "The maximum number of time increment before the solver aborts looking for the equilibrium", GH_ParamAccess.item, 10000);
            pManager.AddIntegerParameter("Max Peak Reset", "max peak (/)", "A peak of kinetic energy corresponds to a configuration with the minimum potential energy, hence the equilibrium. At each peak of kinetic energy, the velocity of each degree of freedom is reset to 0. This parameter allows to set the maximum number of kinetic energy reset before the solver aborts looking for the equilibrium", GH_ParamAccess.item, 1000);
            pManager.AddNumberParameter("Mass Amplification", "Ampl (/)", "The fictitious mass can be amplified in case the DR solver faces convergence issue", GH_ParamAccess.item, 1);
            pManager.AddNumberParameter("Minimum Mass", "Min (kg)", "The minimum fictitious mass applied on the degrees of freedom with 0 fictitious mass", GH_ParamAccess.item, 0.005);

            pManager[1].Optional = true;
            pManager[2].Optional = true;
            pManager[3].Optional = true;
            pManager[4].Optional = true;
            pManager[5].Optional = true;
            pManager[6].Optional = true;
            pManager[7].Optional = true;
            pManager[8].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure containing the total results.", GH_ParamAccess.item);
            pManager.AddBooleanParameter("IsInEquilibrium", "Equilibrium", "True if the external load are in equilibrium with the internal forces.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Time Step", "it (/)", "The number of time increments required to reach the equilibrium", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Peak Reset", "peaks (/)", "The number of detected peaks at which the kinetic energy has been reset to 0", GH_ParamAccess.item);
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            ///log.Info("Main NONLinear Solver: NEW SOLVE INSTANCE");
            //1) Collect Data
            StructureObj structure = new StructureObj();
            GH_Structure<IGH_Goo> gh_loads_ext = new GH_Structure<IGH_Goo>();
            GH_Structure<IGH_Goo> gh_loads_prestress = new GH_Structure<IGH_Goo>();
            double residual0Threshold = -1;
            double dt = -1;
            int maxTimeStep = -1;
            int maxKEReset = -1;
            double amplMass = -1;
            double minMass = -1;

            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetDataTree(1, out gh_loads_ext)) { }
            if (!DA.GetDataTree(2, out gh_loads_prestress)) { }
            if (!DA.GetData(3, ref residual0Threshold)) { }
            if (!DA.GetData(4, ref dt)) { }
            if (!DA.GetData(5, ref maxTimeStep)) { }
            if (!DA.GetData(6, ref maxKEReset)) { }
            if (!DA.GetData(7, ref amplMass)) { }
            if (!DA.GetData(8, ref minMass)) { }

            //2) Format datas before sending and solving in python
            StructureObj new_structure = structure.Duplicate(); //a) Duplicate the structure. The elements still contains the Initial Tension forces. The nodes are in their previously equilibrated coordinates with previous load already applied on it.


            bool success1 = RegisterPointLoads(new_structure, gh_loads_ext.FlattenData()); // new_structure.LoadsToApply was filled with the loads
            bool success2 = RegisterPrestressLoads(new_structure, gh_loads_prestress.FlattenData()); // new_structure.LengtheningsToApply was filled with the length variations

            new_structure.Residual0Threshold = residual0Threshold;
            new_structure.DR = new DRMethod(dt, amplMass, minMass, maxTimeStep, maxKEReset);

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

            SharedData data = new SharedData(new_structure); //Object data contains all the essential informations of structure
            SharedSolverResult result = new SharedSolverResult();

            if (AccessToAll.pythonManager != null) // run calculation in python by transfering the data base as a string. 
            {
                ///log.Debug("pythonManager exists");
                string result_str = null;
                string Data_str = JsonConvert.SerializeObject(data, Formatting.None);
                ///log.Info("Main NonLinear Solver: ask Python to execute a command");

                result_str = AccessToAll.pythonManager.ExecuteCommand(AccessToAll.MainDRSolve, Data_str);

                ///log.Info("Main NonLinear Solver: received results");
                try
                {
                    JsonConvert.PopulateObject(result_str, result);
                }
                catch
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Something went wrong while solving: " + result_str);
                    ///log.Warn("Main NonLinear Solver: Something went wrong while solving:" + result_str);
                    result = null;
                }
            }

            new_structure.PopulateWithSolverResult(result); // Update the new structure, the elements and the nodes with the results of python. 

            GH_StructureObj gh_structure = new GH_StructureObj(new_structure);
            DA.SetData(0, gh_structure);
            DA.SetData(1, new_structure.IsInEquilibrium);
            DA.SetData(2, new_structure.DR.nTimeStep);
            DA.SetData(3, new_structure.DR.nKEReset);

            ///log.Info("Main NONLinear Solver: END SOLVE INSTANCE");
        }

        private bool RegisterPointLoads(StructureObj new_structure, List<IGH_Goo> datas)
        {
            //return true if at least one load is added on the structure
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            //new_structure.LoadsToApply = new List<Vector3d>(); //this is already done in Duplicate
            //foreach (var node in new_structure.StructuralNodes) new_structure.LoadsToApply.Add(new Vector3d(0.0, 0.0, 0.0)); // initialize the LoadsToApply vector with 0 load for each DOF. 


            List<Node> nodes = new_structure.StructuralNodes; //use a shorter nickname 

            PointLoad load;
            foreach (var data in datas)
            {
                if (data is GH_PointLoad)
                {
                    load = ((GH_PointLoad)data).Value; //retrieve the pointload inputted by the user

                    // we need to know on which point or node the load will have to be applied
                    int ind = -1;
                    if (load.NodeInd != -1) //PointsLoad can be defined on a point or on a node index
                    {
                        ind = load.NodeInd;
                    }
                    else // load may have been defined on a point not on a node
                    {
                        if (!Node.EpsilonContains(nodes, load.Point, new_structure.ZeroTol, out ind)) //try to find the point between all nodes
                        {
                            AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "A point Load is applied on a point which does not belong to the structure. This point load is ignored.");
                            continue;//go to next point load
                        }
                    }
                    new_structure.LoadsToApply[ind] += load.Vector; //If Point Load is applied on a node of the structure, then the load is added to all the Loads to apply on the structure. 
                    success = true;
                }
            }
            return success;
        }

        private bool RegisterPrestressLoads(StructureObj new_structure, List<IGH_Goo> datas)
        {
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            //new_structure.LengtheningsToApply = new List<double>();
            //foreach (var elem in new_structure.StructuralElements) new_structure.LengtheningsToApply.Add(0.0); // initialize the LengtheningsToApply vector with 0m length change for each element. 

            //List<Node> nodes = new_structure.StructuralNodes;
            List<Element> elements = new_structure.StructuralElements;

            ImposedLenghtenings DL;
            foreach (var data in datas)
            {
                if (data is GH_ImposedLengthenings)
                {
                    DL = ((GH_ImposedLengthenings)data).Value; //the prestressload is a variation of length

                    int ind_e = DL.Element.Ind;

                    new_structure.LengtheningsToApply[ind_e] += DL.Value; //The variation of length is added to the force to all the lengthenings to apply on the structure. 
                    success = true;
                }
            }
            return success; // if at least one lengthening will be applied on the structure
        }
    }
}
