// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

using System;
using System.Drawing;
using System.Collections.Generic;
using Grasshopper.GUI.Gradient;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using Muscle.View;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.Display
{
    public class ShowForces : GH_Component
    {

        #region Constructors
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public ShowForces()
          : base("ShowForces", "ShowF",
              "Show the internal forces in the structures",
              GHAssemblyName, Folder7_Display)
        {
            gradient_forces = new GH_Gradient_Forces();
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("b921cf0d-fcdf-48a2-8d1e-b35c8a995251"); }
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
            pManager.AddLineParameter("Lines", "L", "Lines", GH_ParamAccess.list);
            pManager.AddNumberParameter("Forces", "F", "Forces in the lines", GH_ParamAccess.list);
            pManager.AddIntegerParameter("Tension Thickness", "tT", "Maximum thickness of the lines in tension. All lines have the same thickness if tT=0.", GH_ParamAccess.item, 2);
            pManager.AddIntegerParameter("Compression Thickness", "tC", "Maximum thickness of the lines in compression. All lines have the same thickness if tC=0.", GH_ParamAccess.item, 2);
            pManager.AddIntegerParameter("Value Settings", "v", "values to show (0 = no value ; 1 = extremes only ; 2 = all values)  ", GH_ParamAccess.item, 2);
            pManager.AddNumberParameter("Text Size", "size", "Size of the text", GH_ParamAccess.item, 0.1);
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
        }

        #endregion Constructors

        #region Properties

        //results
        private List<Line> lines;
        private List<GH_Number> GH_forces;
        private List<double> forces;
        double forceMin, forceMax;

        //color
        private List<double> ColorParams;
        private GH_Gradient_Forces gradient_forces;

        //thickness
        private List<int> WeightParams;
        private int user_thick_max_tension; //fix the maximum thickness of the lines in tension
        private int user_thick_max_compression; //fix the maximum thickness of the lines in compression
        private int thick_max; //= thick_min + user_thick_max
        private int thick_min = 3; //fix the minimum thickness of the lines

        //tags
        private List<int> ind_extremes;
        private int v_setting; //(0 = no value ; 1 = extremes only ; 2 = all values)
        private int d_setting = MuscleConfig.DisplayDecimals;
        private double text_size = 10;




        #endregion Properties


        #region Methods 

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            lines = new List<Line>();
            GH_forces = new List<GH_Number>();

            //collect inputs
            if (!DA.GetDataList(0, lines)) { return; }
            if (!DA.GetDataList(1, GH_forces)) { return; }
            if (!DA.GetData(2, ref user_thick_max_tension)) { }
            if (!DA.GetData(3, ref user_thick_max_compression)) { }
            if (!DA.GetData(4, ref v_setting)) { }
            if (!DA.GetData(5, ref text_size)) { }

            //control of input thickness
            if (user_thick_max_tension < 0) { user_thick_max_tension = 0; }
            if (user_thick_max_compression < 0) { user_thick_max_compression = 0; }
            thick_max = Math.Max(user_thick_max_tension, user_thick_max_compression) + thick_min;

            //control of input value_setting 
            if (v_setting < 0) { v_setting = 0; }
            if (v_setting > 2) { v_setting = 2; }

            //initialize colors weights and tags
            InitColorsWeightsTags();

        }

        /// <summary>
        /// Map the force values to colors and weights of the lines
        /// To do so, we need to know the max and min forces as well as their associated lines. This is why we collect the lines as list and not as items.
        /// </summary>
        public void InitColorsWeightsTags()
        {

            // 1) we find the min and max value of the forces
            forceMin = 0;
            forceMax = 0;
            forces = new List<double>();
            foreach (GH_Number gh_force in GH_forces)
            {
                if (gh_force == null)
                {
                    forces.Add(double.NaN);
                    continue;
                }
                double force = (double)gh_force.Value;
                forces.Add(force);
                if (force <= forceMin) { forceMin = force; }
                if (force >= forceMax) { forceMax = force; }
            }

            // 2) we initialize all required data before drawing

            ind_extremes = new List<int>(); //in order to know to which line is associated the extreme force

            ColorParams = new List<double>();
            WeightParams = new List<int>();

            for (int i = 0; i < forces.Count; i++)
            {
                double force = forces[i];

                //initialise extreme for tags
                if (force == forceMax || force == forceMin)
                {
                    ind_extremes.Add(i);
                }

                //initialise colors and weights for drawing lines
                double aColorParam = ForceToColorParam(force, forceMin, forceMax);
                ColorParams.Add(aColorParam);
                int aWeightParam = ForceToWeightParam(force, forceMin, forceMax);
                WeightParams.Add(aWeightParam);
            }
        }


        /// <summary>
        /// Map a force value to a number between -1 (Red : compression), 0 (white: 0) and 1 (Blue : Tension)
        /// </summary>
        public double ForceToColorParam(double aForce, double forceMin, double forceMax)
        {
            if (aForce <= 0) { return -Math.Abs(aForce / forceMin); } // -1 = Red = compression max
            else { return Math.Abs(aForce / forceMax); } // 1 = Blue = Tension max

            //double span = forceMax - forceMin;
            //double param = (aForce - forceMin) / span; // 0 = Blue = compression and 1 = Red = Tension
            //return 1-(double)param; // 0 = Blue = Tension and 1 = Red = compression
        }

        /// <summary>
        /// Map the absolute value of a force to a integer between thick_min and thick_max
        /// </summary>
        public int ForceToWeightParam(double aForce, double forceMin, double forceMax)
        {

            double absMax = Math.Max(Math.Abs(forceMin), Math.Abs(forceMax));
            double param = Math.Abs(aForce) / absMax; // param is between 0 and 1
            
            // Use different thickness parameters based on whether the force is tension or compression
            int user_thick_max = (aForce >= 0) ? user_thick_max_tension : user_thick_max_compression;
            
            double amplified_param = thick_min + param * user_thick_max; // param is between thick_min and thick_max
            int ceil = (int)Math.Ceiling(amplified_param); // param is rounded up to the nearest int
            int floor = (int)Math.Floor(amplified_param); // param is rounded down to the nearest int

            if (amplified_param - floor >= 0.5) { return ceil; } //1.6 return 2; 1.5 return 2
            return floor; //else return the rounded down value
        }

        /// <summary>
        /// show on a Tag the value of the force for the line i
        /// </summary>
        /// <param name="args"></param> preview object
        /// <param name="i"></param> index of the line and of the force
        public void DrawTag(IGH_PreviewArgs args, int i)
        {
            if (lines == null) return;
            if (forces == null) return;
            Point3d midpoint = lines[i].PointAt(0.5);

            Plane plane;
            args.Viewport.GetCameraFrame(out plane);
            plane.Origin = midpoint;

            //double pixelsPerUnit;
            //args.Viewport.GetWorldToScreenScale(midpoint, out pixelsPerUnit);

            double force_value = (double)Math.Round(forces[i], d_setting, MidpointRounding.AwayFromZero);
            string force_txt = string.Format("{0}", force_value);
            Color color;
            if (force_value < 0) { color = Color.Red; }
            else { color = Color.Blue; }

            args.Display.Draw3dText(force_txt, color, plane, text_size, "Lucida Console"); //text_size / pixelsPerUnit
        }

        /// <summary>
        /// Draw the lines with their associated colors and weights
        /// </summary>
        public override void DrawViewportWires(IGH_PreviewArgs args)
        {
            GH_Gradient gradient = gradient_forces.gradient;
            if (lines == null) return;
            if (ColorParams == null) return;
            if (WeightParams == null) return;
            for (var i = 0; i < lines.Count; i++)
            {
                try
                {
                    args.Display.DrawLine(lines[i], gradient.ColourAt(ColorParams[i]), WeightParams[i]);
                }
                catch
                {
                    continue;
                }
            }
        }






        /// <summary>
        /// Draw the Tags showing the value of the forces. (0 = no value ; 1 = extremes only ; 2 = all values)
        /// </summary>
        public override void DrawViewportMeshes(IGH_PreviewArgs args)
        {
            d_setting = MuscleConfig.DisplayDecimals; //number of decimals

            if (v_setting == 0) { return; } //Abort if user decided to show no values

            else if (v_setting == 1) //show only extreme values
            {
                for (int e = 0; e < ind_extremes.Count; e++)
                {
                    int i = ind_extremes[e];
                    DrawTag(args, i);
                }

            }
            else //show all points
            {
                for (int i = 0; i < lines.Count; i++)
                {
                    DrawTag(args, i);
                }
            }
        }


        #endregion Methods 



    }
}