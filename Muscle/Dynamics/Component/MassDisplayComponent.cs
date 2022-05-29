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
    public class MassDisplayComponent : GH_Component
    {
        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public MassDisplayComponent()
          : base("Dynamic Masses Display", "DMD",
                "Display the dynamic masses contained in the structure.","Muscles", "Dynamics")
        {
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                return Properties.Resources.Mass;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("e942a7a9-5b7f-4c41-bf91-fe0c15d7199c"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "Struct.", "A structure which has already been dynamically calculated.", GH_ParamAccess.item);
         


        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Point Mass", "Point Mass (kg/node)", "Point masses used for the dynamic computation.", GH_ParamAccess.list);
            
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            
            //1) Collect Data
            StructureObj structure = new StructureObj();
            
            //Obtain the data if the component is connected
            if (!DA.GetData(0, ref structure)) { return; }

            //Return the list containing the point masses objects
            DA.SetDataList(0, structure.PointMasses);

        }
       
    }
}

