using GH_IO.Serialization;
using Grasshopper.Kernel.Types;
using System;
using System.Collections.Generic;


namespace Muscles.Materials
{
    public class GH_Muscles_Material : GH_Goo<Muscles_Material>
    {

        #region Properties

        public override bool IsValid { get { return Value.IsValid; } }

        public override string IsValidWhyNot
        {
            get
            {
                if (Value.Name == null)                                                   // Invalid name
                {
                    return "Material name is null.";
                }
                else if (Value.Fy < 0.0)                                                  // Invalid yield strength
                {
                    return "Yield strength is less than 0.0 N/m^2.";
                }
                else if (Value.E < 0.0)                                               // Invalid young modulus
                {
                    return "Young modulus is less than 0.0 N/m^2.";
                }
                else if (Value.Rho < 0.0)                                                 // Invalid density
                {
                    return "Density is less than 0.0 kg/m^3.";
                }
                else                                                                // Type is probably valid
                {
                    return string.Empty;
                }
            }
        }

        /// <summary>
        /// Get a description of the type.
        /// </summary>
        public override string TypeDescription { get { return "Properties of a Material"; } }

        public override string TypeName { get { return "Material"; } }

        public override Muscles_Material Value { set; get; }

        #endregion Properties

        #region Constructors

        public GH_Muscles_Material()
        {
            Value = new Muscles_Material();
        }

        public GH_Muscles_Material(Muscles_Material mat) : base(mat)
        {
            Value = mat;
        }

        public GH_Muscles_Material(GH_Goo<Muscles_Material> other) : base(other)
        {
            Value = other.Value;
        }

        public override IGH_Goo Duplicate()
        {
            return new GH_Muscles_Material((GH_Goo<Muscles_Material>)this);
        }

        #endregion Constructors

        #region Methods

        public override bool CastFrom(object source)
        {
            string text;
            if (source is null) { return false; }
            if (source is string)
            {
                text = (string)source;
                try
                {
                    List<string> characteristics = new List<string>(text.Split(new char[4] { ' ', ',', '-', '_' }));

                    bool removed = false;
                    do
                    {
                        removed = characteristics.Remove("");
                    } while (removed);

                    if (characteristics.Count != 4)
                    {
                        return false;
                    }
                    else
                    {
                        string name = characteristics[0];
                        double fy = Convert.ToSingle(characteristics[1]) * 1e6;
                        double young = Convert.ToSingle(characteristics[2]) * 1e6;
                        double rho = Convert.ToSingle(characteristics[3]);

                        Value = new Muscles_Material(name, young, fy, rho);

                        return true;
                    }
                }
                catch { return false; }
            }
            return false;
        }

        public override bool CastTo<Q>(ref Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(Muscles_Material)))
            {
                object mat = Value;
                target = (Q)mat;
                return true;
            }
            target = default;

            return false;
        }




        public override bool Read(GH_IReader reader)
        {
            string name = reader.GetString("name");
            double fy = reader.GetDouble("fy");
            double young = reader.GetDouble("young");
            double rho = reader.GetDouble("rho");

            Value = new Muscles_Material(name, young, fy, rho);

            return base.Read(reader);
        }

        public override object ScriptVariable()
        {
            return this;
        }

        public override string ToString()
        {
            return Value.ToString();
        }

        public override bool Write(GH_IWriter writer)
        {
            writer.SetString("name", Value.Name);
            writer.SetDouble("fy", Value.Fy);
            writer.SetDouble("young", Value.E);
            writer.SetDouble("rho", Value.Rho);

            return base.Write(writer);
        }

        #endregion Methods

    }
}