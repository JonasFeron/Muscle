using System;
using System.Drawing;
using System.Collections.Generic;
//using System.Windows.Forms;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;

/* Modification non fusionnée à partir du projet 'Muscle (net48)'
Ajouté :
using Muscle;
using Muscle.Elements;
using Muscle.GHModel;
*/
using Muscle.ViewModel;

namespace Muscle.GHModel
{
    public class GH_Element : GH_GeometricGoo<Element>, IGH_PreviewData
    {

        #region Fields

        bool displayInMeshes = true;

        #endregion Fields

        #region Properties

        public override BoundingBox Boundingbox
        {
            get
            {
                BoundingBox bBox = Value.Line.BoundingBox;
                if (Value.IsValid)
                {
                    bBox.Inflate(Value.CS_Main.Dimension * 0.75);
                }

                return bBox;
            }
        }

        public BoundingBox ClippingBox { get { return Boundingbox; } }
        public override string TypeDescription { get { return "An Finite Element may be a cable, a strut, a Element or a general element."; } }

        public override string TypeName
        {
            get
            {

                return Value.TypeName;
            }
        }
        public override Element Value // The Geometry object is accessible from the Value property of the GH_Geometry
        {
            get { return base.Value; }
            set
            {
                if (value is Cable)
                {
                    base.Value = value as Cable;
                }
                if (value is Strut)
                {
                    base.Value = value as Strut;
                }
                if (value is Bar)
                {
                    base.Value = value as Bar;
                }
                base.Value = value;
            }
        }

        #endregion Properties

        #region Constructors

        public GH_Element()
        {
            Value = new Element();
        }

        public GH_Element(Element e)
        {
            Value = e;
        }
        //public GH_Element(Bar b)
        //{
        //    Value = b;
        //}
        //public GH_Element(Strut s)
        //{
        //    Value = s;
        //}
        //public GH_Element(Cable c)
        //{
        //    Value = c;
        //}
        public GH_Element(GH_Goo<Element> gh_e)
        {
            Value = gh_e.Value;
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
            //if (source is Line)
            //{
            //    Line line = source as Line;
            //    Value.Line = line;
            //}
            if (source is GH_Line)
            {
                GH_Line gh_line = source as GH_Line;
                Value.Line = gh_line.Value;
            }
            if (source is Cable)
            {
                Cable e = source as Cable;
                Value = e;
            }
            if (source is Strut)
            {
                Strut e = source as Strut;
                Value = e;
            }
            if (source is Bar)
            {
                Bar e = source as Bar;
                Value = e;
            }
            if (source is Element)
            {
                Element e = source as Element;
                Value = e;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(out Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(Line)))
            {
                object line = Value.Line;
                target = (Q)line;
                return true;
            }

            if (typeof(Q).IsAssignableFrom(typeof(GH_Line)))
            {
                object line = Value.Line;
                target = (Q)(object)new GH_Line((Line)line);
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(Line)))
            {
                object line = Value.Line;
                target = (Q)line;
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(Cable)))
            {
                object e = Value;
                target = (Q)e;
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(Strut)))
            {
                object e = Value;
                target = (Q)e;
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(Bar)))
            {
                object e = Value;
                target = (Q)e;
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(Element)))
            {
                object e = Value;
                target = (Q)e;
                return true;
            }

            target = default;

            return false;
        }


        public void DrawViewportMeshes(GH_PreviewMeshArgs args)
        {
            if (Value.IsValid)
            {
                //try 
                //{ 
                //Extrusion lineWireFrame = new Extrusion();
                //lineWireFrame.AddInnerProfile(Value.CS_Main.InnerProfile(Value.Line.From, new Plane(Value.Line.From, Value.Line.UnitTangent)));
                //lineWireFrame.SetOuterProfile(Value.CS_Main.OuterProfile(Value.Line.From, new Plane(Value.Line.From, Value.Line.UnitTangent)), true);

                //Color color = Color.Gray; // if Element or Bar
                //if (Value is Strut) { color = Color.Red; }
                //if (Value is Cable) { color = Color.Blue;}
                //args.Pipeline.DrawExtrusionWires(lineWireFrame, color);
                //}
                //catch
                //{
                //    //do nothing
                //}
            }
        }



        public void DrawViewportWires(GH_PreviewWireArgs args)
        {
            //args.Pipeline.DrawLine(Value.Line, Color.Green);
        }

        public override IGH_GeometricGoo DuplicateGeometry()
        {
            return new GH_Element(this);
        }

        public override BoundingBox GetBoundingBox(Transform xform)
        {
            if (Value == null) { return BoundingBox.Empty; }

            BoundingBox bBox = xform.TransformBoundingBox(Value.Line.BoundingBox);
            if (Value.IsValid)
            {
                bBox.Inflate(Value.CS_Main.Dimension * 0.75);
            }

            return bBox;
        }

        public override IGH_GeometricGoo Morph(SpaceMorph xmorph)
        {
            GH_Element Element = new GH_Element(this);
            LineCurve lc = new LineCurve(Element.Value.Line);
            xmorph.Morph(lc);
            Element.Value.Line = lc.Line;

            return Element;
        }

        public void RenderModeClick(object sender, EventArgs e)
        {
            displayInMeshes = !displayInMeshes;
        }

        public override string ToString()
        {
            return Value.ToString();
        }

        public override IGH_GeometricGoo Transform(Transform xform)
        {
            GH_Element Element = new GH_Element(this);
            Element.Value.Line.Transform(xform);

            return Element;
        }

        #endregion Methods

    }
}