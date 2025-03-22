using System;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using MuscleApp.ViewModel;

namespace Muscle.View
{
    public class GH_Node : GH_Goo<Node> //: GH_GeometricGoo<Node>, IGH_PreviewData 
    {

        #region Fields

        // bool displayInMeshes = true;

        #endregion Fields

        #region Properties

        //public override BoundingBox Boundingbox
        //{
        //    get
        //    {

        //        BoundingBox bBox = Value.Coordinates.BoundingBox;
        //        if (Value.IsValid)
        //        {
        //            bBox.Inflate(Value.CS.Dimension * 0.75);
        //        }

        //        return bBox;
        //    }
        //}

        //public BoundingBox ClippingBox { get { return Boundingbox; } }
        public override string TypeDescription { get { return "A Node is a point3d with additional structural data"; } }

        public override string TypeName { get { return Value.TypeName; } }
        public override bool IsValid { get { return Value.IsValid; } }
        public override Node Value 
        {
            get { return base.Value; }
            set
            {
                base.Value = value;
            }
        }

        #endregion Properties

        #region Constructors

        public GH_Node()
        {
            Value = new Node();
        }

        public GH_Node(Node n)
        {
            Value = n;
        }
        public GH_Node(GH_Goo<Node> gh_n)
        {
            Value = gh_n.Value;
        }


        #endregion Constructors

        //public override bool AppendMenuItems(ToolStripDropDown menu)
        //{
        //    Menu_AppendItem(menu, "Display in 3D.", RenderModeClick, displayInMeshes);
        //    Menu_AppendItem(menu, "Display with lines.", RenderModeClick, !displayInMeshes);
        //    return base.AppendMenuItems(menu);
        //}

        #region Methods

        public override bool CastFrom(object source)
        {
            if (source == null) { return false; }
            if (source is GH_Point)
            {
                GH_Point gh_point = source as GH_Point;
                Value.Coordinates = gh_point.Value;
            }
            if (source is Node)
            {
                Node n = source as Node;
                Value = n;
            }
            // Handle the case when a Node is wrapped in a GH_ObjectWrapper
            if (source is GH_ObjectWrapper wrapper && wrapper.Value is Node)
            {
                Value = (Node)wrapper.Value;
                return true;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(ref Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(Point3d)))
            {
                object n = Value.Coordinates;
                target = (Q)n;
                return true;
            }

            if (typeof(Q).IsAssignableFrom(typeof(GH_Point)))
            {
                object n = Value.Coordinates;
                target = (Q)(object)new GH_Point((Point3d)n);
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(Node)))
            {
                object n = Value;
                target = (Q)n;
                return true;
            }

            target = default;

            return false;
        }


        //public void DrawViewportMeshes(GH_PreviewMeshArgs args)
        //{
        //    if(Value.IsValid)
        //    {
        //        Extrusion lineWireFrame = new Extrusion();
        //        lineWireFrame.AddInnerProfile(Value.CS_Main.InnerProfile(Value.Line.From, new Plane(Value.Line.From, Value.Line.UnitTangent)));
        //        lineWireFrame.SetOuterProfile(Value.CS_Main.OuterProfile(Value.Line.From, new Plane(Value.Line.From, Value.Line.UnitTangent)), true);

        //        Color color = Color.Gray; // if Element or Bar
        //        if (Value is Strut) { color = Color.Red; }
        //        if (Value is Cable) { color = Color.Blue; }

        //        args.Pipeline.DrawExtrusionWires(lineWireFrame, color);
        //    }

        //}

        //public void DrawViewportWires(GH_PreviewWireArgs args)
        //{
        //    args.Pipeline.DrawLine(Value.Line, Color.Green);
        //}

        public override IGH_Goo Duplicate()
        {
            return new GH_Node(this);
        }

        //public override IGH_GeometricGoo DuplicateGeometry()
        //{
        //    return new GH_Node(this);
        //}

        //public override BoundingBox GetBoundingBox(Transform xform)
        //{
        //    if (Value == null) { return BoundingBox.Empty; }

        //    BoundingBox bBox = xform.TransformBoundingBox(Value.Line.BoundingBox);
        //    if (Value.IsValid)
        //    {
        //        bBox.Inflate(Value.CS_Main.Dimension * 0.75);
        //    }

        //    return bBox;
        //}

        //public override IGH_GeometricGoo Morph(SpaceMorph xmorph)
        //{
        //    GH_Element Element = new GH_Element(this);
        //    LineCurve lc = new LineCurve(Element.Value.Line);
        //    xmorph.Morph(lc);
        //    Element.Value.Line = lc.Line;

        //    return Element;
        //}

        //public void RenderModeClick(object sender, EventArgs e)
        //{
        //    displayInMeshes = !displayInMeshes;
        //}

        public override string ToString()
        {
            return Value.ToString();
        }

        //public override IGH_GeometricGoo Transform(Transform xform)
        //{
        //    GH_Element Element = new GH_Element(this);
        //    Element.Value.Line.Transform(xform);

        //    return Element;
        //}

        #endregion Methods

    }
}