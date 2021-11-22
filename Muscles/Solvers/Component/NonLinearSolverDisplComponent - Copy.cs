using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscles.Elements;
using Muscles.Loads;
using Muscles.Nodes;
using Muscles.PythonLink;
using Muscles.PythonLink.Component;
using Muscles.Structure;
using Newtonsoft.Json;
using Rhino.Geometry;

namespace Muscles.Solvers
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
                "  Displacement method is used (solve K.U=L then post-process to find axial forces) with the following assumptions:\n" +
                "  L=Le+Lp : Application of external (Le) and prestress (Lp) point loads altogether. It is advised to apply Le and Lp successively in 2 Solver components.\n" +
                "  Incremental solver : Loads L are splitted in +- n_it increments Li which are applied successively (K.Ui=Li) with arclength constraints\n" +
                "  K=Km+Kg : Addition of material (Km) and geometric (Kg) stiffness matrices (recomputed at each increment).\n" +
                "  Only forces coming from previous solutions are considered in (first) Kg. Axial prestress P are not considered in Kg.\n" +
                "  N=Q+P : After the last iteration, addition of the post-processed axial forces Q with the prestress forces P .",
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
            get { return new Guid("91c4f69c-748a-4ef7-b1d4-a16c6455f1f8"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may contain previous results (forces and displacements).", GH_ParamAccess.item);
            pManager.AddGenericParameter("External Point Loads", "Le (kN)", "The external point loads to apply on the structure.", GH_ParamAccess.tree);
            pManager.AddGenericParameter("Axial Prestress", "P (kN)", "The prestress forces to apply on the structure.\n Axial Prestress P are converted into point loads Lp which are applied on the structure.\n Axial prestress P are added to the resulted forces Q at the end (N=Q+P).", GH_ParamAccess.tree);
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
            StructureObj new_structure = structure.Deformed(); //a) Duplicate structure and update its nodes coordinates with results from previous solve

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

            SharedData data = new SharedData(new_structure,n_it); //Object data contains all the essential informations of structure
            SharedSolverResult result = new SharedSolverResult();

            if (AccessToAll.pythonManager != null) // run calculation in python by transfering the data base as a string. 
            {
                log.Debug("pythonManager exists");
                string result_str = null;
                string Data_str = JsonConvert.SerializeObject(data, Formatting.None);
                log.Info("Main NonLinear Solver: ask Python to execute a command");

                result_str = AccessToAll.pythonManager.ExecuteCommand(AccessToAll.Main_NonLinearSolve, Data_str);

                log.Info("Main NonLinear Solver: received results");
                try
                {
                    JsonConvert.PopulateObject(result_str, result);
                }
                catch
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Something went wrong while solving: " + result_str);
                    log.Warn("Main NonLinear Solver: Something went wrong while solving:" + result_str);
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
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            List<Node> nodes = new_structure.StructuralNodes;

            PointLoad load;
            foreach (var data in datas)
            {
                if (data is GH_PointLoad)
                {
                    load = ((GH_PointLoad)data).Value;
                    int ind = -1;
                    if (load.NodeInd != -1)
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
                    nodes[ind].LoadToApply += load.Vector; //If Point Load is applied on a node of the structure, then the load is added to Loads to apply on this node. 
                    success = true;
                }
            }
            return success;
        }

        private bool RegisterPrestressLoads(StructureObj new_structure, List<IGH_Goo> datas)
        {
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            List<Node> nodes = new_structure.StructuralNodes;
            List<Element> elements = new_structure.StructuralElements;

            PrestressLoad P;
            foreach (var data in datas)
            {
                if (data is GH_PrestressLoad)
                {
                    P = ((GH_PrestressLoad)data).Value;

                    int ind_e = P.Element.Ind;
                    int ind_n0 = P.Element.EndNodes[0];
                    int ind_n1 = P.Element.EndNodes[1];

                    elements[ind_e].LengtheningToApply += P.Value; //The prestress load is added to the force to apply on this element. 
                    nodes[ind_n0].LoadToApply += P.AsPointLoad0.Vector; //The prestress as point loads are added to the pointload to apply on the element extremitites. 
                    nodes[ind_n1].LoadToApply += P.AsPointLoad1.Vector;
                    success = true;
                }
            }
            return success;
        }
    }
}