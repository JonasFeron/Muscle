using GH_IO.Serialization;
using Grasshopper.Kernel.Types;
using Muscles.Materials;

namespace Muscles.CrossSections
{
    public class GH_CrossSection : GH_Goo<ICrossSection>
    {

        #region Properties

        public override bool IsValid { get { return Value.IsValid; } }

        public override string IsValidWhyNot
        {
            get
            {
                if (Value.Dimension <= 0) { return "Dimension is less than or equal to 0.0cm"; }
                if (Value.Thickness <= 0) { return "Thickness is less than or equal to 0.0cm"; }
                if (Value.Thickness > Value.Dimension / 2.0) { return "Thickness is greater than physically possible."; }

                return string.Empty;
            }
        }

        public override string TypeDescription { get { return "Cross section of a structural element."; } }
        public override string TypeName { get { return Value.ShapeName; } }

        public override ICrossSection Value { get => base.Value; set => base.Value = value; }

        #endregion Properties

        #region Constructors

        public GH_CrossSection()
        {
            Value = new CS_Circular();
        }

        public GH_CrossSection(ICrossSection cs) : base(cs)
        {
            Value = cs;
        }

        public GH_CrossSection(GH_Goo<ICrossSection> other) : base(other)
        {
            Value = other.Value;
        }

        #endregion Constructors

        #region Methods

        public override bool CastFrom(object source)
        {
            if (source is ICrossSection)
            {
                ICrossSection cs = source as ICrossSection;
                Value = cs;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(ref Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(ICrossSection)))
            {
                object cs = Value;
                target = (Q)cs;
                return true;
            }

            target = default(Q);

            return false;
        }

        public override IGH_Goo Duplicate()
        {
            return new GH_CrossSection(this);
        }

        //public override bool Read(GH_IReader reader) //used in Cross Section Parameter
        //{
        //    string TypeName = reader.GetString("type name");

        //    if (TypeName == "Circle cross section")
        //    {
        //        double diameter = reader.Getdouble("dimension");
        //        double thickness = reader.Getdouble("thickness");
        //        Value = new CS_Circular(diameter, thickness);
        //    }
        //    else if (TypeName == "Square cross section")
        //    {
        //        double diameter = reader.Getdouble("dimension");
        //        double thickness = reader.Getdouble("thickness");
        //        Value = new CS_Square(diameter, thickness);
        //    }
        //    else { return false; }

        //    return base.Read(reader);
        //}

        public override object ScriptVariable()
        {
            return Duplicate();
        }

        public override string ToString()
        {
            return Value.ToString();
        }
        //public override bool Write(GH_IWriter writer)
        //{
        //    writer.SetString("type name", Value.ShapeName);
        //    writer.Setdouble("dimension", Value.Dimension);
        //    writer.Setdouble("thickness", Value.Thickness);


        //    return base.Write(writer);
        //}

        #endregion Methods

    }
}