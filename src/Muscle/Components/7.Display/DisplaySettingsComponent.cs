using System;
using System.Drawing;
using System.Collections.Generic;
using Grasshopper.GUI.Gradient;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using Muscle.Util;
using Grasshopper.Kernel.Data;
using MuscleApp;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Display
{
    public class DisplaySettingsComponent : GH_Component
    {

        #region Constructors
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public DisplaySettingsComponent()
          : base("DisplaySettings", "Display",
              "Set the display of your structure",
              GHAssemblyName, Folder7_Display)
        {

        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("e65e6f09-2b23-4669-a652-b955b0902cbe"); }
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
                return null;
            }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddNumberParameter("Supports Size", "Spt", "Set the amplification factor on the size of supports", GH_ParamAccess.item, 1.0);
            pManager[0].Optional = true;
            pManager.AddNumberParameter("Loads Size", "Load", "Set the amplification factor on the size of loads", GH_ParamAccess.item, 1.0);
            pManager[1].Optional = true;
            pManager.AddNumberParameter("Prestress Size", "Prestress", "Set the amplification factor on the size of prestress", GH_ParamAccess.item, 1.0);
            pManager[2].Optional = true;
            pManager.AddIntegerParameter("Decimal", "Decimal", "Set the amount of decimal to display", GH_ParamAccess.item, 1);
            pManager[3].Optional = true;
            pManager.AddVectorParameter("Gravity", "g (m/s²)", "Vector representing the acceleration due to gravity in m/s²", GH_ParamAccess.tree, new Vector3d(0, 0, -9.81));
            pManager[4].Optional = true;
            // pManager.AddNumberParameter("Dynamic Mass scale", "Dyn. Mass scale", "Set the amplification factor on the size of supports", GH_ParamAccess.item, 1.0);
            // pManager[5].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
        }

        #endregion Constructors

        #region Properties


        #endregion Properties


        #region Methods 

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            double spt = 1.0;
            double load = 1.0;
            double prestress = 1.0;
            int _decimal = 1;
            // double scale_dyn = 1.0;
            GH_Structure<GH_Vector> gravity = new GH_Structure<GH_Vector>();

            //collect inputs
            if (!DA.GetData(0, ref spt)) { }
            if (!DA.GetData(1, ref load)) { }
            if (!DA.GetData(2, ref prestress)) { }
            if (!DA.GetData(3, ref _decimal)) { }
            if (!DA.GetDataTree(4, out gravity)) { }
            // if (!DA.GetData(5, ref scale_dyn)) { }

            MuscleConfig.DisplaySupportAmpli = spt;
            MuscleConfig.DisplayLoadAmpli = load;
            MuscleConfig.DisplayPrestressAmpli = prestress;
            MuscleConfig.DisplayDecimals = _decimal;
            // MuscleConfig.DisplayMassAmpli = scale_dyn; //Considered for the scaling of the display of the masses considered for the dynamic computation 
            OnPingDocument().ExpirePreview(true); //it is better to only expire the solution of the GH_Support component

            List<GH_Vector> gravities = gravity.FlattenData();
            if (gravities.Count > 1)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Please enter only one acceleration vector.");
                return;
            }
            if (gravities.Count == 1)
            {
                MuscleAppConfig.g = gravities[0].Value;
                OnPingDocument().ExpireSolution();
            }

        }




        #endregion Methods 



    }
}
