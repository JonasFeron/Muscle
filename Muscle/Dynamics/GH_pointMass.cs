using Grasshopper.Kernel.Types;
using Grasshopper.Kernel;
using Rhino.Geometry;
using System.Drawing;
using GH_IO.Serialization;
using System;
using Muscle.Loads;
using Muscle.Dynamics;


namespace Muscle.Dynamics
{
    public class GH_PointLoad : GH_GeometricGoo<PointLoad>
    {
        public GH_PointLoad() : base()
        {
            Value = new PointLoad();
        }

        public GH_PointLoad(PointLoad mass) : base(mass)
        {
            Value = mass;
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
        
        public override string TypeName { get { return "Point mass"; } }

        public override string TypeDescription { get { return "Point mass to apply on the node of a structure."; } }

        private Color red = Color.Red;

        public BoundingBox ClippingBox { get { return Boundingbox; } }

        public void DrawViewportMeshes(GH_PreviewMeshArgs args)
        {
            double DisplayMassAmpli = AccessToAll.DisplayDyn;

            Vector3d v_display = Value.Vector * DisplayMassAmpli; //scale x [m] = x[kg]/10kg * LoadAmpliFactor



            double height = Math.Abs(v_display.Z / 4);
            double radius = height / 2.5;
            args.Pipeline.DrawCone(new Cone(new Plane(Value.Point, new Vector3d(0.0, 0.0, 1.0)), height, radius), red);
            //Sphere Sph = new Sphere(Value.Point, radius);
            //args.Pipeline.DrawSphere(Sph,red);
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
