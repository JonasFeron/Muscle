using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using System.Collections.Generic;
using System.Threading;
using System;

namespace Muscle.ViewModel
{
    /// <summary>
    /// An Element is the most general (bi-)linear elastic structural element. 
    /// </summary>
    public class Element
    {
        #region Properties
        public int Idx { get; set; } //index of the element in the structure
        public string Name { get; set; }
        public int Type { get; set; } //-1 if supposed in compression, 1 if supposed in tension. 0 if both.
        public Line Line { get; set; } // the line with a current length in the current state
        public List<int> EndNodes { get; set; } //index of the end nodes of the element
        public double FreeLength { get; set; } // [m] - the Free length of the element
        public virtual ICrossSection CS { get; set; } //used for calculating volume and displaying the Element in GH. 
        public virtual BilinearMaterial Material { get; set; } //used for calculating mass and strength

        public double V //m3
        {
            get
            {
                return FreeLength * CS.Area;
            }
        }
        public double Mass//kg
        {
            get
            {
                return V * Material.Rho;
            }
        }
        // public Vector3d Weight { get { return AccessToAll.g * Mass; } } //N

        public bool IsValid
        {
            get
            {
                if (CS.IsValid && Material.IsValid && Line.IsValid && UC >= 0 && UC <= 1) return true;
                else return false;
            }
        }

        public double Tension { get; set; } //[N]



        ///// Strength /////

        public string BucklingLaw { get; set; }
        public double kb { get; set; } //buckling factor
        public double Lambda
        {
            get
            {
                double Lb = kb * FreeLength; //[m] - buckling length based on the free length of the element
                double A = CS.Area;
                double I = CS.Inertia;
                return Lb * Math.Sqrt(A / I);
            }
        }
        public double Lambda_E
        {
            get
            {
                double Ec = Material.Ec;
                double Fy = -Material.Fyc;
                return Math.PI * Math.Sqrt(Ec / Fy);
            }
        }

        public double Lambda_Adim
        {
            get
            {
                return Lambda / Lambda_E;
            }
        }

        private double Alpha //imperfection factor of buckling law
        {
            get
            {
                switch (BucklingLaw)
                {
                    case "a":
                        {
                            return 0.21;
                        }
                    case "b":
                        {
                            return 0.34;
                        }
                    case "c":
                        {
                            return 0.49;
                        }
                    case "d":
                        {
                            return 0.76;
                        }
                }
                return 0;
            }
        }

        private double Phi
        {
            get
            {
                return 0.5 * (1 + Alpha * (Lambda_Adim - 0.2) + Math.Pow(Lambda_Adim, 2));
            }
        }

        private double Xsi_EC3
        {
            get
            {
                double xsi = 1 / (Phi + Math.Sqrt(Math.Pow(Phi, 2) - Math.Pow(Lambda_Adim, 2)));
                if (xsi <= 1) return xsi;
                else if (xsi > 1.0) return 1.0;
                else return 0.0;
            }
        }

        public double Xsi
        {
            get
            {
                switch (BucklingLaw)
                {
                    case "Euler":
                        {
                            double xsi = 1 / Math.Pow(Lambda_Adim, 2);
                            if (xsi <= 1) return xsi;
                            else return 1.0;
                        }
                    case "Rankine":
                        {
                            return 1 / (1 + Math.Pow(Lambda_Adim, 2));
                        }
                    case "a":
                        {
                            return Xsi_EC3;
                        }
                    case "b":
                        {
                            return Xsi_EC3;
                        }
                    case "c":
                        {
                            return Xsi_EC3;
                        }
                    case "d":
                        {
                            return Xsi_EC3;
                        }
                    case "Slack":
                        {
                            return 0.0;
                        }
                }
                return 1.0; // return yielding in all other cases !
            }
        }

        /// <summary>
        /// Buckling strength of the material in compression.
        /// </summary>
        protected double Fyb
        {
            get
            {
                double Fyc = Material.Fyc;
                return Xsi * Fyc;
            }
        }
        public virtual Interval AllowableStress
        {
            get
            {
                return new Interval(Fyb, Material.Fyt);
            }
        }
        public Interval AllowableTension
        {
            get
            {
                double Fyt = AllowableStress.T1;
                double Fyb = AllowableStress.T0;
                return new Interval(Fyb * CS.Area, Fyt * CS.Area);
            }
        }
        public virtual double UC
        {
            get
            {
                try
                {
                    if (Tension >= 0) return Tension / AllowableTension.T1;
                    else return Tension / AllowableTension.T0;
                }
                catch (DivideByZeroException)
                {
                    if (Tension >= 0) return double.PositiveInfinity;
                    else return double.NegativeInfinity;
                }
            }
        }



        #endregion Properties

        #region Constructors
        private void Init()
        {
            Idx = -1;
            Name = "General Element";
            Type = -1;
            Line = new Line();
            FreeLength = -1.0;
            EndNodes = new List<int>();
            CS = new CS_Circular();
            Material = new BilinearMaterial();
            BucklingLaw = "Yielding";
            kb = 1.0;
            Tension = 0;
        }


        public Element()
        {
            Init();
        }

        public Element(Line aLine, ICrossSection aCS, BilinearMaterial aMat, string name, int type, string buckling_law, double buckling_factor)
        {
            Init();
            Line = aLine;
            FreeLength = aLine.Length; // Use the length of the inputted line as the free length
            CS = aCS.Copy();
            Material = aMat.Copy();
            Name = name;
            Type = type;
            BucklingLaw = buckling_law;
            kb = buckling_factor;
            if (kb <= 0) kb = 0;
            if (BucklingLaw == "Slack") Material.Ec = 0; // cancel compression stiffness. Buckling strength will also be set to 0.
        }


        public Element(Element other) // Copy constructor. This allows to create a new Element and modify it, without alterating the original
        {
            Name = other.Name;
            Type = other.Type;
            Line = other.Line;
            FreeLength = other.FreeLength;
            EndNodes = other.EndNodes;
            CS = other.CS.Copy();
            Material = other.Material.Copy();
            BucklingLaw = other.BucklingLaw;
            kb = other.kb;
            Idx = other.Idx;
            Tension = other.Tension;
        }

        
        #endregion Constructors

        #region Methods

        public Element Copy()
        {
            return new Element(this);
        }
        public Element CopyAndUpdate(double FreeLength, double Tension)
        {
            Element copy = new Element(this);
            copy.FreeLength = FreeLength;
            copy.Tension = Tension;
            return copy;
        }

        public override string ToString()
        {
            //if (this is Cable) return (this as Cable).ToString();
            //if (this is Strut) return (this as Strut).ToString();
            //if (this is Bar) return (this as Bar).ToString();
            return $"{Name} {Idx} with free length {FreeLength:F3}m and mass {Mass:F1}kg.\n    In Compression : A={CS.Area * 1e6:F0}mm^2, E={Material.Ec * 1e-6:F0}MPa.\n   In Tension : A={CS.Area * 1e6:F0}mm^2, E={Material.Et * 1e-6:F0}MPa.";
        }




        #endregion Methods

    }
}