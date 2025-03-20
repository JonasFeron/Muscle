using Grasshopper.Kernel.Types;
using Grasshopper.Kernel;
using Rhino.Geometry;
using System.Drawing;
using GH_IO.Serialization;
using System;
using MuscleApp.ViewModel;

namespace Muscle.View
{
    public class GH_PointLoad : GH_GeometricGoo<PointLoad>, IGH_PreviewData
    {
        public GH_PointLoad() : base()
        {
            Value = new PointLoad();
        }

        public GH_PointLoad(PointLoad load) : base(load)
        {
            Value = load;
        }

        public GH_PointLoad(GH_PointLoad other)
        {
            Value = other.Value.Duplicate();
        }

        public override BoundingBox Boundingbox
        {
            get
            {
                BoundingBox bBox = new Line(Value.Point, -10.0 * Value.Vector / Value.Vector.Length, 10.0).BoundingBox;
                bBox.Inflate(1.0);
                return bBox;
            }
        }

        public override string TypeName { get { return "Point load"; } }

        public override string TypeDescription { get { return "Point load to apply on the node of a structure."; } }

        private Color green = Color.Green;

        public BoundingBox ClippingBox { get { return Boundingbox; } }

        public void DrawViewportMeshes(GH_PreviewMeshArgs args)
        {
            double DisplayLoadAmpli = MuscleConfig.DisplayLoadAmpli;

            Vector3d v_display = Value.Vector * DisplayLoadAmpli / 10000.0;             //scale x [m] = x[kN]/10kN * LoadAmpliFactor

            if (Math.Abs(v_display.X / v_display.Length) >= 0.001)
            {
                double height = Math.Abs(v_display.X / 4);
                double radius = height / 2.5;
                args.Pipeline.DrawCone(new Cone(new Plane(Value.Point, new Vector3d(1.0, 0.0, 0.0)), height, radius), green);
            }
            if (Math.Abs(v_display.Y / v_display.Length) >= 0.001)
            {
                double height = Math.Abs(v_display.Y / 4);
                double radius = height / 2.5;
                args.Pipeline.DrawCone(new Cone(new Plane(Value.Point, new Vector3d(0.0, 1.0, 0.0)), height, radius), green);
            }
            if (Math.Abs(v_display.Z / v_display.Length) >= 0.001)
            {
                double height = Math.Abs(v_display.Z / 4);
                double radius = height / 2.5;
                args.Pipeline.DrawCone(new Cone(new Plane(Value.Point, new Vector3d(0.0, 0.0, 1.0)), height, radius), green);
            }
        }

        public void DrawViewportWires(GH_PreviewWireArgs args)
        {

            double DisplayLoadAmpli = MuscleConfig.DisplayLoadAmpli;
            int _decimal = MuscleConfig.DisplayDecimals;


            Point3d node = Value.Point;

            Plane plane;
            args.Viewport.GetCameraFrame(out plane);

            double pixelsPerUnit;
            args.Viewport.GetWorldToScreenScale(node, out pixelsPerUnit);

            Vector3d v_display = Value.Vector * DisplayLoadAmpli / 10000.0;             //scale x [m] = x[kN]/10kN * LoadAmpliFactor

            string load_X = string.Format("{0}", Math.Round(Value.Vector.X / 1000, _decimal, MidpointRounding.AwayFromZero));
            string load_Y = string.Format("{0}", Math.Round(Value.Vector.Y / 1000, _decimal, MidpointRounding.AwayFromZero));
            string load_Z = string.Format("{0}", Math.Round(Value.Vector.Z / 1000, _decimal, MidpointRounding.AwayFromZero));


            if (Math.Abs(v_display.X / v_display.Length) >= 0.001)
            {
                Vector3d V = new Vector3d(v_display.X, 0, 0);
                Point3d start = node - V;
                plane.Origin = start;
                args.Pipeline.DrawLine(new Line(start, V), green, 2);
                args.Pipeline.Draw3dText(load_X, green, plane, 14 / pixelsPerUnit, "Lucida Console");
            }
            if (Math.Abs(v_display.Y / v_display.Length) >= 0.001)
            {
                Vector3d V = new Vector3d(0, v_display.Y, 0);
                Point3d start = node - V;
                plane.Origin = start;
                args.Pipeline.DrawLine(new Line(start, V), green, 2);
                args.Pipeline.Draw3dText(load_Y, green, plane, 14 / pixelsPerUnit, "Lucida Console");
            }
            if (Math.Abs(v_display.Z / v_display.Length) >= 0.001)
            {
                Vector3d V = new Vector3d(0, 0, v_display.Z);
                Point3d start = node - V;
                plane.Origin = start;
                args.Pipeline.DrawLine(new Line(start, V), green, 2);
                args.Pipeline.Draw3dText(load_Z, green, plane, 14 / pixelsPerUnit, "Lucida Console");
            }
        }

        public override IGH_GeometricGoo DuplicateGeometry()
        {
            return new GH_PointLoad(this);
        }

        public override BoundingBox GetBoundingBox(Transform xform)
        {
            return xform.TransformBoundingBox(Boundingbox);
        }

        public override IGH_GeometricGoo Morph(SpaceMorph xmorph)
        {
            GH_PointLoad nGHPointLoad = new GH_PointLoad(this);
            nGHPointLoad.Value.Point = xmorph.MorphPoint(Value.Point);
            nGHPointLoad.Value.Vector = new Vector3d(xmorph.MorphPoint(new Point3d(Value.Vector)));

            return nGHPointLoad;
        }

        public override string ToString()
        {
            return Value.ToString();
        }

        public override IGH_GeometricGoo Transform(Transform xform)
        {
            GH_PointLoad nGHPointLoad = new GH_PointLoad(this);
            nGHPointLoad.Value.Point.Transform(xform);
            nGHPointLoad.Value.Vector.Transform(xform);

            return nGHPointLoad;
        }
    }
}