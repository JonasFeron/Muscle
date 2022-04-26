using System;
using System.Drawing;
using System.Collections.Generic;
using Grasshopper.GUI.Gradient;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using Muscles_ADE.Util;
using Grasshopper.Kernel.Data;

namespace Muscles_ADE.Display
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
              "Muscles", "Display")
        {

        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("05f27814-8558-4f01-91c5-28db10c2fcc3"); }
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
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddNumberParameter("Supports Size", "Spt", "Set the amplification factor on the size of supports", GH_ParamAccess.item, 1.0);
            pManager[0].Optional = true;
            pManager.AddNumberParameter("Loads Size", "Load", "Set the amplification factor on the size of loads", GH_ParamAccess.item, 1.0);
            pManager[1].Optional = true;
            pManager.AddIntegerParameter("Decimal", "Decimal", "Set the amount of decimal to display", GH_ParamAccess.item, 1);
            pManager[2].Optional = true;
            pManager.AddVectorParameter("Gravity", "g (m/s²)", "Vector representing the acceleration due to gravity in m/s²", GH_ParamAccess.tree, new Vector3d(0, 0, -9.81));
            pManager[3].Optional = true;
            pManager.AddVectorParameter("Gravity", "g (m/s²)", "Vector representing the acceleration due to gravity in m/s²", GH_ParamAccess.tree, new Vector3d(0, 0, -9.81));
            pManager[3].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
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
            int _decimal = 1;
            GH_Structure<GH_Vector> gravity = new GH_Structure<GH_Vector>();

            //collect inputs
            if (!DA.GetData(0, ref spt)) { }
            if (!DA.GetData(1, ref load)) { }
            if (!DA.GetData(2, ref _decimal)) { }
            if (!DA.GetDataTree(3, out gravity)) { }


            AccessToAll.DisplaySupportAmpli = spt;
            AccessToAll.DisplayLoadAmpli = load;
            AccessToAll.DisplayDecimals = _decimal;

            this.OnPingDocument().ExpirePreview(true); //it is better to only expire the solution of the GH_Support component

            List<GH_Vector> gravities = gravity.FlattenData();
            if (gravities.Count > 1)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Please enter only one acceleration vector.");
                return;
            }
            if (gravities.Count == 1)
            {
                AccessToAll.g = gravities[0].Value;
                this.OnPingDocument().ExpireSolution();
            }

        }


        ///// <summary>
        ///// show on a Tag the value of the force for the line i
        ///// </summary>
        ///// <param name="args"></param> preview object
        ///// <param name="i"></param> index of the line and of the force
        //public void DrawTag(IGH_PreviewArgs args, int i)
        //{
        //    if (lines == null) return;
        //    if (forces == null) return;
        //    Point3d midpoint = lines[i].PointAt(0.5);

        //    Plane plane;
        //    args.Viewport.GetCameraFrame(out plane);
        //    plane.Origin = midpoint;

        //    double pixelsPerUnit;
        //    args.Viewport.GetWorldToScreenScale(midpoint, out pixelsPerUnit);

        //    double force_value = (double)Math.Round(forces[i], d_setting, MidpointRounding.AwayFromZero);
        //    string force_txt = String.Format("{0}", force_value);
        //    Color color;
        //    if (force_value < 0) { color = Color.Red; }
        //    else { color = Color.Blue; }

        //    args.Display.Draw3dText(force_txt, color, plane, 14 / pixelsPerUnit, "Lucida Console");
        //}

        ///// <summary>
        ///// Draw the lines with their associated colors and weights
        ///// </summary>
        //public override void DrawViewportWires(IGH_PreviewArgs args)
        //{
        //    GH_Gradient gradient = gradient_forces.gradient;
        //    if (lines == null) return;
        //    if (ColorParams == null) return;
        //    if (WeightParams == null) return;
        //    for (var i = 0; i < lines.Count; i++)
        //    {
        //        try
        //        {
        //            args.Display.DrawLine(lines[i], gradient.ColourAt(ColorParams[i]), WeightParams[i]);
        //        }
        //        catch
        //        {
        //            continue;
        //        }
        //    }
        //}






        ///// <summary>
        ///// Draw the Tags showing the value of the forces. (0 = no value ; 1 = extremes only ; 2 = all values)
        ///// </summary>
        //public override void DrawViewportMeshes(IGH_PreviewArgs args)
        //{
        //    if (v_setting == 0) { return; } //Abort if user decided to show no values

        //    else if(v_setting == 1) //show only extreme values
        //    {
        //        for (int e = 0; e < ind_extremes.Count; e++)
        //        {
        //            int i = ind_extremes[e];
        //            DrawTag(args, i);
        //        }

        //    }
        //    else //show all points
        //    {
        //        for (int i = 0; i < lines.Count; i++)
        //        {
        //            DrawTag(args, i);
        //        }
        //    }
        //}


        #endregion Methods 



    }
}
