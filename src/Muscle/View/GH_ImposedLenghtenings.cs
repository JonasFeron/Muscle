using Grasshopper.Kernel.Types;
using Muscle.ViewModel;

namespace Muscle.View
{
    class GH_ImposedLengthenings : GH_Goo<ImposedLenghtenings>
    {
        #region Properties


        //public bool IsPreviewCapable { get { return true; } } //to implement 

        public override ImposedLenghtenings Value { set; get; }
        public override bool IsValid { get { return Value.IsValid; } }

        public override string TypeDescription { get { return "Initial force in the element considering that all nodes are fixed in space."; } }

        public override string TypeName { get { return "Prestress"; } }



        #endregion Properties

        #region Constructors

        public GH_ImposedLengthenings() : base()
        {
            Value = new ImposedLenghtenings();
        }

        public GH_ImposedLengthenings(ImposedLenghtenings prestress) : base(prestress)
        {
            Value = prestress;
        }

        public GH_ImposedLengthenings(GH_Goo<ImposedLenghtenings> gh_prestress)
        {
            Value = gh_prestress.Value.Duplicate();
        }
        public override IGH_Goo Duplicate()
        {
            return new GH_ImposedLengthenings(this);
        }

        #endregion Constructors


        #region Methods

        public override bool CastFrom(object source)
        {
            if (source == null) { return false; }

            if (source is Element)
            {
                Value.Element = (Element)source;
                return true;
            }


            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(ref Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(ImposedLenghtenings)))
            {
                object initialforce = Value;
                target = (Q)initialforce;
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(double)))
            {
                object force = Value.Value;
                target = (Q)force;
                return true;
            }

            if (typeof(Q).IsAssignableFrom(typeof(Element)))
            {
                object e = Value.Element;
                target = (Q)e;
                return true;
            }

            target = default;

            return false;
        }

        //public void DrawViewportMeshes(GH_PreviewMeshArgs args)  
        //{
        //    // To Implement : (first inherit from GHGeometricGoo ? ) aim is to show the force on the element

        //}

        //public void DrawViewportWires(GH_PreviewWireArgs args)
        //{
        //    args.Pipeline.DrawPoint(Value.Point, System.Drawing.Color.Blue);
        //    //args.Pipeline.DrawArrow(new Line(Value.Point, new Vector3d(4, 5, 6), 10), Color.Orange); // this arrow can be used to represent the reaction forces
        //}



        public override object ScriptVariable()
        {
            return Value;
        }

        public override string ToString()
        {
            return Value.ToString();
        }
        #endregion Methods

    }
}