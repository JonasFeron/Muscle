using Grasshopper.Kernel.Types;
using Grasshopper.Kernel;
using Rhino.Geometry;
using System.Drawing;
using GH_IO.Serialization;
using System;
using Muscle.Loads;


namespace Muscle.View
{   


    //Create a GH element for the masses used for the dynamic computation
    public class GH_PointMass : GH_GeometricGoo<PointMass>, IGH_PreviewData 
    {
        public GH_PointMass() : base()
        {
            Value = new PointMass();
        }

        public GH_PointMass(PointMass mass) : base(mass)
        {
            Value = mass;
        }

        public GH_PointMass(GH_PointMass other)
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
            //Take the value of 'DisplayDyn' in the AccessToAll file to adapt the size of the displayed masses (sphere)
            double DisplayMassAmpli = AccessToAll.DisplayDyn;

            Vector3d v_display = Value.Vector * DisplayMassAmpli; //scale x [m] = x[kg]/10kg * LoadAmpliFactor

            if (Math.Abs(v_display.Z / v_display.Length) >= 0.001)
            {
                //Sphere to display at each node
                double radius = Math.Abs(v_display.Z / 10);
                Sphere sph = new Sphere(Value.Point,radius);
                args.Pipeline.DrawSphere(sph, red);

            }
        }
        
        public void DrawViewportWires(GH_PreviewWireArgs args)
        {

            double DisplayMassAmpli = AccessToAll.DisplayDyn;
            int _decimal = AccessToAll.DisplayDecimals;


            Point3d node = Value.Point;

            Plane plane;
            args.Viewport.GetCameraFrame(out plane);

            double pixelsPerUnit;
            args.Viewport.GetWorldToScreenScale(node, out pixelsPerUnit);
        }

        public override IGH_GeometricGoo DuplicateGeometry()
        {
            return new GH_PointMass(this);
        }

        public override BoundingBox GetBoundingBox(Transform xform)
        {
            return xform.TransformBoundingBox(Boundingbox);
        }

        public override IGH_GeometricGoo Morph(SpaceMorph xmorph)
        {
            GH_PointMass nGHPointMass = new GH_PointMass(this);
            nGHPointMass.Value.Point = xmorph.MorphPoint(Value.Point);
            nGHPointMass.Value.Vector = new Vector3d(xmorph.MorphPoint(new Point3d(Value.Vector)));

            return nGHPointMass;
        }

        public override string ToString()
        {
            return Value.ToString();
        }

        public override IGH_GeometricGoo Transform(Transform xform)
        {
            GH_PointMass nGHPointMass = new GH_PointMass(this);
            nGHPointMass.Value.Point.Transform(xform);
            nGHPointMass.Value.Vector.Transform(xform);

            return nGHPointMass;
        }
    }
}
