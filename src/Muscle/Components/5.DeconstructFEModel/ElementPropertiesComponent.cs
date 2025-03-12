using System;
using System.Collections.Generic;

using Grasshopper.Kernel;
using Muscle.ViewModel;
using Rhino.Geometry;

namespace Muscle.Components.ModelProperties
{
    public class ElementPropertiesComponent : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ElementPropertiesComponent()
          : base("Element Properties", "Elem prop",
              "Get the properties of elements.",
              "Muscles", "Elements")
        {
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Element", "E", "The finite element(s).", GH_ParamAccess.item); //0
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddTextParameter("Type", "type", "General, Bar, Strut or Cable.", GH_ParamAccess.item); //0
            pManager.AddIntegerParameter("Element Index", "Ind", "The indexes of the structural elements.", GH_ParamAccess.item); //1
            pManager.AddIntegerParameter("Nodes Indexes", "End nodes", "The indexes of the elements end nodes.", GH_ParamAccess.list); //2
            pManager.AddLineParameter("Line", "L", "The current line geometry with the current length of the finite element.", GH_ParamAccess.item); //3
            pManager.AddNumberParameter("Free length", "Free L (m)", "The length of the element free of any strain.", GH_ParamAccess.item); //4
            pManager.AddGenericParameter("Main Cross Section", "Main CS", "The main cross section used for the calculation of the volume and for linear analysis.", GH_ParamAccess.item); //5
            pManager.AddGenericParameter("Cross Sections List", "List CS", "The cross sections used in non-linear finite element analysis.\n The list contains [CS in compression, CS in Tension].", GH_ParamAccess.list); //6
            pManager.AddGenericParameter("Main Material", "Main Mat", "The main material used for the calculation of the mass and for linear analysis.", GH_ParamAccess.item); //7
            pManager.AddGenericParameter("Material List", "List Mat", "The materials used in non-linear finite element analysis.\n The list contains [Mat in compression, Mat in Tension].", GH_ParamAccess.list); //8
            pManager.AddNumberParameter("Volume", "V (m³)", "Volume in m³.", GH_ParamAccess.item); //9
            pManager.AddNumberParameter("Mass", "m (kg)", "Mass in kg.", GH_ParamAccess.item); //10
            pManager.AddVectorParameter("Weight", "W (kN)", "Weight in kN", GH_ParamAccess.item); //11
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
