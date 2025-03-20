using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using MuscleApp.ViewModel;
using static Muscle.Components.GHComponentsFolders;
using Rhino.Geometry;

namespace Muscle.Components.DeconstructFEModel
{
    public class DeconstructElementComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DeconstructElementComponent()
          : base("Deconstruct Element", "DeElem",
              "Deconstruct an element.",
              GHAssemblyName, Folder5_DeconstructFEM)
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "Input finite element", GH_ParamAccess.item); //0
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Name", "name", "Element name", GH_ParamAccess.item); //0
            pManager.AddIntegerParameter("Element Index", "Idx", "Index of the element", GH_ParamAccess.item); //1
            pManager.AddIntegerParameter("End nodes indexes", "End nodes", "Indexes of the end nodes", GH_ParamAccess.list); //2
            pManager.AddLineParameter("Line", "L", "Current line and current length of the element", GH_ParamAccess.item); //3
            pManager.AddNumberParameter("Free length", "Lfree (m)", "Free length of the element", GH_ParamAccess.item); //4
            pManager.AddGenericParameter("Cross Section", "CS", "Cross section of the element", GH_ParamAccess.item); //5
            pManager.AddGenericParameter("Material", "M", "Bilinear Material of the element", GH_ParamAccess.item); //6
            pManager.AddVectorParameter("Weight", "W (kN)", "Self-Weight (kN) of the element", GH_ParamAccess.item); //7
            pManager.AddNumberParameter("Tension", "t (kN)", "Axial force (kN, tension positive, compression negative) in the element due to all applied loads and prestress", GH_ParamAccess.item); //8
            pManager.AddIntervalParameter("Resistances", "[tmin, tmax] (kN)", "Resistance interval [(-)Buckling resistance, (+)Yielding resistance] (kN)", GH_ParamAccess.item); //9
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            Element e = new Element();

            if (!DA.GetData(0, ref e)) { return; } // si j'arrive à collectionner des elements, je les stocke dans elements, sinon je termine et je renvoie rien.

            DA.SetData(0, e.TypeName);
            DA.SetData(1, e.Ind);
            DA.SetDataList(2, e.EndNodes);
            DA.SetData(3, e.Line);
            DA.SetData(4, e.LFree);

            DA.SetData(5, e.CS_Main);

            List<ICrossSection> CS = new List<ICrossSection> { e.CS_Comp, e.CS_Tens };
            DA.SetDataList(6, CS);

            DA.SetData(7, e.Mat_Main);

            List<Muscles_Material> Mat = new List<Muscles_Material> { e.Mat_Comp, e.Mat_Tens };
            DA.SetDataList(8, Mat);

            DA.SetData(9, e.V);
            DA.SetData(10, e.Mass);
            DA.SetData(11, e.Weight / 1000);
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
            get { return new Guid("83c5746d-d54d-4f88-b553-0d4cbe86bac8"); }
        }
    }
}
