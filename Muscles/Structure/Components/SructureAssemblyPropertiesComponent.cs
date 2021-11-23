using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;

namespace Muscles.Structure
{
    public class SructureAssemblyPropertiesComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public SructureAssemblyPropertiesComponent()
          : base("Sructure - Assembly Properties", "Struct Properties",
              "Get the properties of the assembled structure",
              "Muscles", "Model")
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
            get { return new Guid("ad6d7f8d-5013-4869-8e7f-25b62e49e2d0"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A finite elements Model.", GH_ParamAccess.item);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddIntegerParameter("Rank", "r", "Rank of equilibrium matrix", GH_ParamAccess.item); //0
            pManager.AddNumberParameter("S", "S", "Eigen values of equilibrium matrix", GH_ParamAccess.list); //1
            pManager.AddNumberParameter("A", "A", "Equilibrium matrix", GH_ParamAccess.tree); //2
            pManager.AddIntegerParameter("StaticDeg", "s", "Degree of static indeterminacy", GH_ParamAccess.item); //3
            pManager.AddNumberParameter("Self-Stress", "SS", "Self-stress modes of the structure", GH_ParamAccess.tree); //4
            pManager.AddIntegerParameter("KinematicDeg", "m", "Degree of kinematic indeterminacy, or i.e. number of mechanisms (infinitesimal and rigid body)", GH_ParamAccess.item); //5
            pManager.AddNumberParameter("Mechanisms", "Um", "Mechanisms of the structure", GH_ParamAccess.tree); //6
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            GH_StructureObj gh_struct = new GH_StructureObj();

            if (!DA.GetData(0, ref gh_struct)) { return; }

            //DA.SetData(0, gh_struct.Value.AssemblyResult.r);
            //DA.SetDataList(1, gh_struct.Value.AssemblyResult.S);
            //DA.SetDataTree(2, gh_struct.A);
            //DA.SetData(3, gh_struct.Value.AssemblyResult.s);
            //DA.SetDataTree(4, gh_struct.SS);
            //DA.SetData(5, gh_struct.Value.AssemblyResult.m);
            //DA.SetDataTree(6, gh_struct.Um_row);
        }
    }
}