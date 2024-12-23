using System;
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscles.Elements;
using Muscles.Nodes;
using Muscles.Structure;
using Rhino.Geometry;

namespace Muscles.Loads
{
    public class SelfStressScenario : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public SelfStressScenario()
          : base("Self-Stress Scenario", "SSS",
              "Turn a Self-Stress STATE into equivalent imposed lenghtenings and shortenings in the elements.\n" +
              "A self-stress STATE is the linear combination of several self-stress MODES with their associated levels. ",
              "Muscles", "Loads")
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
            get { return new Guid("690dae2a-6632-49a6-9e84-54251b1569f5"); }
        }


        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure to self-stress","struct","The structure to apply a self-stress scenario on",GH_ParamAccess.item);
            pManager.AddNumberParameter("Self-Stress modes", "Modes", "All modes (One mode per branch) will be linearly combined with their associated levels to form a self-stress state.", GH_ParamAccess.tree);
            pManager.AddNumberParameter("Self-stress levels", "Levels (kN)", "Define one level in kN per self-stress mode.", GH_ParamAccess.tree);
        }


        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Self-stressed Structure", "struct", "The structure has been self-stressed (linear combination of self-stress modes and levels)", GH_ParamAccess.item);
        }


        protected override void SolveInstance(IGH_DataAccess DA)
        {
            //1) collect datas
            StructureObj structure = new StructureObj();
            GH_Structure<GH_Number> gh_modes = new GH_Structure<GH_Number>();
            GH_Structure<GH_Number> gh_levels = new GH_Structure<GH_Number>();

            if (!DA.GetData(0, ref structure)) { return; } 
            if (!DA.GetDataTree(1, out gh_modes)) { return; } //abort if no inputted modes
            if (!DA.GetDataTree(2, out gh_levels)) { return; } //abort if no inputted levels

            StructureObj structure_output = Combine(structure, gh_modes, gh_levels);
            // 3) output data
            DA.SetData(0, structure_output);

        }



        private StructureObj Combine(StructureObj structure, GH_Structure<GH_Number> gh_modes, GH_Structure<GH_Number> gh_levels)
        {
            StructureObj structure_output = structure.Duplicate();

            int b = structure.StructuralElements.Count; //number of bars
            int n = structure.StructuralNodes.Count;
            List<Element> elements = structure.StructuralElements;
            List<double> prestressForces = Enumerable.Range(0, b).Select(i => 0d).ToList(); // initialize a list of 0.0 of size b
            List<Vector3d> prestressExtLoads = Enumerable.Range(0, n).Select(i => new Vector3d()).ToList();


            // 0 ) check inputs
            int s = gh_modes.Branches.Count;

            if (gh_levels.DataCount != s)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "The number of self-stress modes is different than the number of levels");
                return null;
            }

            // 1) Combine the forces and levels into the total prestress Forces
            for (int m = 0; m<s; m++) // foreach mode
            {
                List<double> mode = gh_modes.Branches[m].Select(i => i.Value).ToList(); // transform gh_mode in a mode (list)
                double level = 1000*gh_levels.FlattenData()[m].Value; //[N]
                if (mode.Count!=b)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Check that the length of each mode = number of elements)");
                    return null;
                }

                for(int i=0; i<b; i++) //foreach element
                {
                    double force = mode[i] * level; 
                    Element elem = elements[i];

                    ImposedLenghtenings DL = new ImposedLenghtenings(elem);
                    DL.Value = DL.Tension2Lengthening(force); //convert the internal force in N into a length variation

                    prestressForces[i] += DL.AsTension; // DL.Value = force. The prestress force is added to the force to apply on this element. 
                    int ind_n0 = DL.Element.EndNodes[0];
                    int ind_n1 = DL.Element.EndNodes[1];
                    prestressExtLoads[ind_n0] += DL.AsPointLoad0.Vector; //The prestress as point loads are added to the pointload to apply on the element extremitites. 
                    prestressExtLoads[ind_n1] += DL.AsPointLoad1.Vector;
                }                
            }

            // 2) Check that the forces correspond to a self-stress, i.e. the sum of all prestressExtloads in each node and each direction is null. 
            bool IsSelfStressed = true;

            double LVL_ref = gh_levels.FlattenData().Select(i => Math.Abs(i.Value*1000)).ToList().Sum(); //sum all the levels together
            double ZeroTol = 1e-3; //[/]

            for (int j = 0; j < n; j++) //foreach node
            {
                if (structure.StructuralNodes[j].isXFree) // if node is free in X, check that the external load due to the self stress force is = 0. 
                {
                    double load_adim = Math.Abs(prestressExtLoads[j].X / LVL_ref);
                    if (load_adim > ZeroTol) IsSelfStressed = false; 
                }
                if (structure.StructuralNodes[j].isYFree) 
                {
                    double load_adim = Math.Abs(prestressExtLoads[j].Y / LVL_ref);
                    if (load_adim > ZeroTol) IsSelfStressed = false;
                }
                if (structure.StructuralNodes[j].isZFree) 
                {
                    double load_adim = Math.Abs(prestressExtLoads[j].Z / LVL_ref);
                    if (load_adim > ZeroTol) IsSelfStressed = false;
                }
            }

            // 3) If the forces correspond to a self-stress -> register the prestress forces in the structure
            if (! IsSelfStressed)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "The inputted prestress forces are not in a self-stress state. To apply these prestressforces, please use a (non)linear solver instead");
                return null;
            }

            for (int i = 0; i < b; i++) //foreach element
            {
                Element e = structure_output.StructuralElements[i];
                double t = prestressForces[i]; 

                ImposedLenghtenings DL = new ImposedLenghtenings(e);
                DL.Value = DL.Tension2Lengthening(t);
                e.Tension += t; //[N] = DL.AsTension
                e.LFree += DL.Value; 
            }
            for (int i = 0; i < n; i++) //foreach node
            {
                Node node = structure_output.StructuralNodes[i];
                Vector3d prestressReaction = -prestressExtLoads[i];
                node.Reaction += prestressReaction; 
            }
            return structure_output;
        }

    }
}