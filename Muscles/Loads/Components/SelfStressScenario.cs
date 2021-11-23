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
              "A self-stress SCENARIO is a self-stress STATE multiplied by a global prestress level (one global level for the whole structure). A self-stress state is the linear combination of several self-stress MODES with their associated levels (one level per mode, usually any number between -1 and 1). ",
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
            pManager.AddGenericParameter("Structure to self-stress","struct","The structure to apply a self-stress on",GH_ParamAccess.item);
            pManager.AddNumberParameter("Self-stress modes", "Modes", "All modes (One mode per branch) will be linearly combined with their associated levels to form a self-stress state.", GH_ParamAccess.tree);
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
            List<double> prestressForces = Enumerable.Range(0, b).Select(i => 0d).ToList();
            List<Vector3d> prestressExtLoads = Enumerable.Range(0, n).Select(i => new Vector3d()).ToList();


            // 0 ) check inputs
            int s = gh_modes.Branches.Count;
            if (structure.AssemblyResult.s != s)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Some self-stress mode have been ignored by user.");
            }
            if (gh_levels.DataCount != s)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "The number of self-stress modes is different than the number of levels");
                return null;
            }

            // 1) Combine the forces and levels into the total prestress Forces
            for (int m = 0; m<s; m++) // foreach mode
            {
                List<double> mode = gh_modes.Branches[m].Select(i => i.Value).ToList();
                double level = gh_levels.FlattenData()[m].Value;
                if (mode.Count!=b)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Check that all modes (one per list) have the same length (=number of elements)");
                    return null;
                }

                
                for(int i=0; i<b; i++) //foreach element
                {
                    double force = mode[i] * level; 
                    Element elem = elements[i];
                    PrestressLoad P = new PrestressLoad(elem,force);

                    prestressForces[i] += P.Value; // P.Value = force. The prestress force is added to the force to apply on this element. 
                    int ind_n0 = P.Element.EndNodes[0];
                    int ind_n1 = P.Element.EndNodes[1];
                    prestressExtLoads[ind_n0] += P.AsPointLoad0.Vector; //The prestress as point loads are added to the pointload to apply on the element extremitites. 
                    prestressExtLoads[ind_n1] += P.AsPointLoad1.Vector;
                }                
            }

            // 2) Check that the forces correspond to a self-stress (A*t = 0)
            bool IsSelfStressed = true;

            double LVL_ref = gh_levels.FlattenData().Select(i => Math.Abs(i.Value)).ToList().Sum(); //sum all the levels together
            double ZeroTol = 1e-3; 

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

            // 3) If the forces correspond to a self-stress -> register the initial forces in the structure
            if (! IsSelfStressed)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "The inputted forces are not a self-stress modes. To apply these forces, please use a (non)linear solver instead");
                return null;
            }

            //for (int i = 0; i < b; i++) //foreach element
            //{
            //    double prev = structure_output.StructuralElements[i].Tension;
            //    double result = prestressForces[i] * 1000;//level is in kN and we register it in N
            //    double total = prev + result; 
            //    structure_output.StructuralElements[i].AxialForce_Results = new List<double>() {result} ;
            //    structure_output.StructuralElements[i].AxialForce_Total = new List<double>() {total};
            //}

            return structure_output;
        }

    }
}