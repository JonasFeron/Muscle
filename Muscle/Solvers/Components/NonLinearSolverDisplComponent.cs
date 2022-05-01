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
    public class NonLinearSolverDisplComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public NonLinearSolverDisplComponent()
          : base("Solver - Non Linear - Displacements Meth.", "Non Linear D",
                "Solve truss with geometric non linearities.\n" +
                "  Displacement method is used (solve K.U=L then post-process to find axial forces). Loads are splitted in n_it increments and are applied one after the other. Length variations are turned into equivalent loads.",
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
            get { return new Guid("1876c337-7fef-4dda-8c3f-69de895e5087"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may contain previous results (forces and displacements).", GH_ParamAccess.item);
            pManager.AddGenericParameter("External Point Loads", "Le (kN)", "The external point loads to apply on the structure.", GH_ParamAccess.tree);
            pManager.AddGenericParameter("Length Variations", "DL (mm)", "Lengthening (+) or shortening (-) to apply on the elements.", GH_ParamAccess.tree);
            pManager.AddIntegerParameter("Number of iterations", "n_it", "Solve non-linearly the structure in +- n_it linear steps", GH_ParamAccess.item, 50);
            pManager[1].Optional = true;
            pManager[2].Optional = true;
            pManager[3].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure containing the results (forces and displacements).", GH_ParamAccess.item);

        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            log.Info("Main NONLinear Solver: NEW SOLVE INSTANCE");
            //1) Collect Data
            StructureObj structure = new StructureObj();
            GH_Structure<IGH_Goo> gh_loads_ext = new GH_Structure<IGH_Goo>();
            GH_Structure<IGH_Goo> gh_loads_prestress = new GH_Structure<IGH_Goo>();
            int n_it = -1;

            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetDataTree(1, out gh_loads_ext)) { }
            if (!DA.GetDataTree(2, out gh_loads_prestress)) { }
            if (!DA.GetData(3, ref n_it)) { }


            //2) Transform datas before solving in python
            StructureObj new_structure = structure.Duplicate(); //a) Duplicate structure and update its nodes coordinates with results from previous solve

            bool success1 = RegisterPointLoads(new_structure, gh_loads_ext.FlattenData());
            bool success2 = RegisterPrestressLoads(new_structure, gh_loads_prestress.FlattenData());

            if (!success1 && !success2)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to collect load data");
                return; //abort if both failed
            }
            //3) Solve in python
            if (AccessToAll.pythonManager == null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Please restart the \"Initialize Python\" Component.");
                DA.SetData(0, null);
                return;
            }

            SharedData data = new SharedData(new_structure, n_it); //Object data contains all the essential informations of structure
            SharedSolverResult result = new SharedSolverResult();

            if (AccessToAll.pythonManager != null) // run calculation in python by transfering the data base as a string. 
            {
                log.Debug("pythonManager exists");
                string resultString = null;
                string dataString = JsonConvert.SerializeObject(data, Formatting.None);
                log.Info("Main NonLinear Solver: ask Python to execute a command");

                resultString = AccessToAll.pythonManager.ExecuteCommand(AccessToAll.MainNonLinearSolve, dataString);

                log.Info("Main NonLinear Solver: received results");
                try
                {
                    JsonConvert.PopulateObject(resultString, result);
                }
                catch
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Something went wrong while solving: " + resultString);
                    log.Warn("Main NonLinear Solver: Something went wrong while solving:" + resultString);
                    result = null;
                }
            }

            new_structure.PopulateWithSolverResult(result);

            GH_StructureObj gh_structure = new GH_StructureObj(new_structure);
            DA.SetData(0, gh_structure);
            log.Info("Main NONLinear Solver: END SOLVE INSTANCE");
        }


        private bool RegisterPointLoads(StructureObj new_structure, List<IGH_Goo> datas)
        {
            //return true if at least one load is added on the structure
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            //new_structure.LoadsToApply = new List<Vector3d>();
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
