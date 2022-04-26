using System.Drawing;
using GH_IO.Serialization;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using Grasshopper.Kernel.Data;
using System.IO;

namespace Muscles_ADE
{
    public class GH_Support : GH_GeometricGoo<Support>, IGH_PreviewData
    {

        #region Properties



        public override bool IsValid { get { return new GH_Point(Value.Point).IsValid; } }

        public override string IsValidWhyNot
        {
            get
            {
                if (!new GH_Point(Value.Point).IsValid) { return "The point of application of the support is invalid."; }

                return String.Empty;
            }
        }

        public override string TypeDescription { get { return "A support may fix the X, Y or Z translations of a node."; } }

        public override string TypeName { get { return "Support"; } }

        public override Support Value { set; get; }

        #endregion Properties

        #region Constructors

        public GH_Support()
        {
            Value = new Support();
        }

        public GH_Support(Support support) : base(support)
        {
            Value = support;
        }

        public GH_Support(GH_GeometricGoo<Support> gh_support)
        {
            Value = gh_support.Value.Duplicate();
        }

        #endregion Constructors

        #region Methods

        public override bool CastFrom(object source)
        {
            if (source == null) { return false; }

            if (source is Point3d)
            {
                Value.Point = (Point3d)source;
                return true;
            }

            if (source is GH_Point)
            {
                Value.Point = ((GH_Point)source).Value;
                return true;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(out Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(Support)))
            {
                object support = Value;
                target = (Q)support;
                return true;
            }

            if (typeof(Q).IsAssignableFrom(typeof(Point3d)))
            {
                object point = Value.Point;
                target = (Q)point;
                return true;
            }

            if (typeof(Q).IsAssignableFrom(typeof(GH_Point)))
            {
                object point = Value.Point;
                target = (Q)(object)new GH_Point((Point3d)point);
                return true;
            }


            target = default(Q);

            return false;
        }
        #region Display
        private static double height = 2.5 * AccessToAll.DisplaySupportAmpli;
        private static double radius = 1.0 * AccessToAll.DisplaySupportAmpli;
        private static double size = Math.Max(height, radius);

        public void DrawViewportMeshes(GH_PreviewMeshArgs args) // draw a cone for each fixed translation 
        {
            height = 2.5 * AccessToAll.DisplaySupportAmpli;
            radius = 1.0 * AccessToAll.DisplaySupportAmpli;
            // TO Implement : size of the cones could be controlled by the user depending on the scale of the model
            if (!Value.isXFree) { args.Pipeline.DrawCone(new Cone(new Plane(Value.Point, new Vector3d(-1.0, 0.0, 0.0)), height, radius), System.Drawing.Color.Blue); }
            if (!Value.isYFree) { args.Pipeline.DrawCone(new Cone(new Plane(Value.Point, new Vector3d(0.0, -1.0, 0.0)), height, radius), System.Drawing.Color.Blue); }
            if (!Value.isZFree) { args.Pipeline.DrawCone(new Cone(new Plane(Value.Point, new Vector3d(0.0, 0.0, -1.0)), height, radius), System.Drawing.Color.Blue); }
        }

        public void DrawViewportWires(GH_PreviewWireArgs args)
        {
            args.Pipeline.DrawPoint(Value.Point, System.Drawing.Color.Blue);
            //args.Pipeline.DrawArrow(new Line(Value.Point, new Vector3d(4, 5, 6), 10), Color.Orange); // this arrow can be used to represent the reaction forces
        }


        public override BoundingBox Boundingbox
        {
            get
            {
                size = Math.Max(height, radius);
                Point3d point = Value.Point;
                BoundingBox boundingBox = new BoundingBox(point, point);
                boundingBox.Inflate(size);

                return boundingBox;
            }
        }

        public BoundingBox ClippingBox { get { return Boundingbox; } }

        public bool Hidden { get; set; }

        public bool IsPreviewCapable { get { return true; } }

        public override IGH_GeometricGoo DuplicateGeometry()
        {
            return new GH_Support(this);
        }

        public override BoundingBox GetBoundingBox(Transform xform)
        {
            size = Math.Max(height, radius);
            Point3d point = Value.Point;
            point.Transform(xform);
            BoundingBox boundingBox = new BoundingBox(point, point);
            boundingBox.Inflate(size);

            return boundingBox;
        }

        public override IGH_GeometricGoo Morph(SpaceMorph xmorph)
        {
            GH_Support morphedSupport = new GH_Support(this);
            Point3d morphedPoint = xmorph.MorphPoint(Value.Point);

            morphedSupport.Value.Point = morphedPoint;

            return morphedSupport;
        }
        public override IGH_GeometricGoo Transform(Transform xform) //when is it called ??!!
        {
            GH_Support transformedSupport = new GH_Support(this); // Create new instance of GH_Support to avoid modifying this one.

            transformedSupport.Value.Point.Transform(xform); // Transform point of the Support stored inside GH_Support.Value.

            return transformedSupport;
        }

        #endregion
        public override bool Read(GH_IReader reader)
        {
            double x = reader.GetSingle("x");
            double y = reader.GetSingle("y");
            double z = reader.GetSingle("z");

            Point3d point = new Point3d(x, y, z);

            bool Xfree = reader.GetBoolean("X");
            bool Yfree = reader.GetBoolean("Y");
            bool Zfree = reader.GetBoolean("Z");

            Value = new Support(point, Xfree, Yfree, Zfree);

            return base.Read(reader);
        }

        public override object ScriptVariable()
        {
            return Value;
        }

        public override string ToString()
        {
            return Value.ToString();
        }



        public override bool Write(GH_IWriter writer)
        {
            writer.SetDouble("x", Value.Point.X);
            writer.SetDouble("y", Value.Point.Y);
            writer.SetDouble("z", Value.Point.Z);

            writer.SetBoolean("X", Value.isXFree);
            writer.SetBoolean("Y", Value.isYFree);
            writer.SetBoolean("Z", Value.isZFree);

            return base.Write(writer);
        }

        /// <summary>
        /// Transform a GH_Structure of IGH_Goo into a list of Support if the input has the correct type
        /// </summary>
        /// <param name="gh_input"></param>
        /// <returns></returns>
        public static List<Support> GHStructureToList(GH_Structure<IGH_Goo> gh_input)
        {
            List<Support> supports = new List<Support>();
            foreach (var branch in gh_input.Branches)
            {
                foreach (var data in branch)
                {
                    if (data is GH_Support)
                    {
                        Support temp;
                        data.CastTo<Support>(out temp);
                        supports.Add(temp);
                    }
                    else
                    {
                        throw new InvalidDataException("Input is not a support");
                    }
                }
            }
            return supports;
        }

        /// <summary>
        /// Transform a GH_Structure of GH_Support into a list of Support
        /// </summary>
        /// <param name="GH_supports"></param>
        /// <returns></returns>
        public static List<Support> GHStructureToList(GH_Structure<GH_Support> GH_supports)
        {
            List<Support> supports = new List<Support>();
            foreach (var branch in GH_supports.Branches)
            {
                foreach (var data in branch)
                {
                    supports.Add(data.Value);
                }
            }
            return supports;
        }

        /// <summary>
        /// Transform a list of Support into a list of GH_Support
        /// </summary>
        /// <param name="supports"></param>
        /// <returns></returns>
        public static List<GH_Support> ListToList_GH(List<Support> supports)
        {
            List<GH_Support> list_GH = new List<GH_Support>();

            foreach (Support support in supports)
            {
                list_GH.Add(new GH_Support(support));
            }
            return list_GH;
        }


        /// <summary>
        /// Transform a user inputted list of GH_support into a list of GH_support which have only one support per point.
        /// </summary>
        /// <param name="gh_input"></param>
        /// <returns></returns>
        public static List<GH_Support> MergeConditionsOnSamePoint(GH_Structure<GH_Support> gh_input)
        {
            List<Support> input = GHStructureToList(gh_input);
            List<Support> merged_supports = Support.MergeConditionsOnSamePoint(input);
            List<GH_Support> merged_gh_supports = ListToList_GH(merged_supports);

            return merged_gh_supports;
        }

        /// <summary>
        /// Transform a user inputted list of GH_support into a list of supports which have only one support per point.
        /// </summary>
        /// <param name="gh_input"></param>
        /// <returns></returns>
        public static List<Support> MergeConditionsOnSamePoint(GH_Structure<IGH_Goo> gh_input)
        {
            List<Support> input = GHStructureToList(gh_input);
            List<Support> merged_supports = Support.MergeConditionsOnSamePoint(input);

            return merged_supports;
        }


        /// <summary>
        /// return a new GH support with merged fixation conditions in X Y and/or Z according to support1 and 2. If Support 1 and 2 are not defined on the same point, the merged support is defined on point1.
        /// </summary>
        /// 
        private static GH_Support MergeConditionsOf(GH_Support support1, GH_Support support2)
        {
            Support merged_support = Support.MergeConditionsOf(support1.Value, support2.Value);

            return new GH_Support(merged_support);
        }


        #endregion Methods
    }
}