using GH_IO.Serialization;
using Grasshopper.Kernel.Types;
using Muscle.ViewModel;
using System;
using System.Collections.Generic;


namespace Muscle.View
{
    public class GH_BilinearMaterial : GH_Goo<BilinearMaterial>
    {

        #region Properties

        public override bool IsValid { get { return Value.IsValid; } }

        public override string IsValidWhyNot
        {
            get
            {
                if (Value.Name == null)                                                   
                {
                    return "Material name is null.";
                }
                else if (Value.Fyc > 0.0)                                                 
                {
                    return "Compressive Yield Strength must be negative.";
                }
                else if (Value.Fyt < 0.0)                                                  
                {
                    return "Tensile Yield Strength must be positive.";
                }
                else if (Value.Ec < 0.0)                                               
                {
                    return "Compressive Young modulus must be positive.";
                }
                else if (Value.Et < 0.0)                                               
                {
                    return "Tensile Young modulus must be positive.";
                }
                else if (Value.Ec == 0.0 && Value.Et == 0.0)                                               
                {
                    return "At least one Young Modulus (Compressive or Tensile) must be different than 0.";
                }
                else if (Value.Rho < 0.0)                                                 
                    return "Specific mass must be positive.";
                }
                else                                                                
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

        public override BilinearMaterial Value { set; get; }

        #endregion Properties

        #region Constructors

        public GH_BilinearMaterial()
        {
            Value = new BilinearMaterial();
        }

        public GH_BilinearMaterial(BilinearMaterial mat) : base(mat)
        {
            Value = mat;
        }

        public GH_BilinearMaterial(GH_Goo<BilinearMaterial> other) : base(other)
        {
            Value = other.Value;
        }

        public override IGH_Goo Duplicate()
        {
            return new GH_BilinearMaterial(this);
        }

        #endregion Constructors

        #region Methods

    
        public override bool CastFrom(object source)
        {
            if (source is null) { return false; }
            if (source is string)
            {
                string text = (string)source;
                try
                {
                    List<string> characteristics = new List<string>(text.Split(new char[4] { ' ', ',', '-', '_' }));

                    bool removed = false;
                    do
                    {
                        removed = characteristics.Remove("");
                    } while (removed);

                    if (characteristics.Count != 6)
                    {
                        return false;
                    }
                    else
                    {
                        string name = characteristics[0];
                        double ec = Convert.ToDouble(characteristics[1]) * 1e6;
                        double et = Convert.ToDouble(characteristics[2]) * 1e6;
                        double fyc = Convert.ToDouble(characteristics[3]) * 1e6;
                        double fyt = Convert.ToDouble(characteristics[4]) * 1e6;
                        double rho = Convert.ToDouble(characteristics[5]);

                        Value = new BilinearMaterial(name, ec, et, fyc, fyt, rho);

                        return true;
                    }
                }
                catch { return false; }
            }
            return false;
        }

        public override bool CastTo<Q>(ref Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(BilinearMaterial)))
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
            double ec = reader.GetDouble("Ec");
            double et = reader.GetDouble("Et");
            double fyc = reader.GetDouble("Fyc");
            double fyt = reader.GetDouble("Fyt");
            double rho = reader.GetDouble("rho");

            Value = new BilinearMaterial(name, ec, et, fyc, fyt, rho);

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
            writer.SetDouble("Ec", Value.Ec);
            writer.SetDouble("Et", Value.Et);
            writer.SetDouble("Fyc", Value.Fyc);
            writer.SetDouble("Fyt", Value.Fyt);
            writer.SetDouble("rho", Value.Rho);

            return base.Write(writer);
        }


        #endregion Methods

    }
}