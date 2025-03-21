using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using System.Collections.Generic;
using System.Threading;
using System;

namespace MuscleApp.ViewModel
{
    /// <summary>
    /// An Element is the most general (bi-)linear elastic structural element. 
    /// </summary>
    public class Element
    {
        #region Properties
        public int Idx { get; set; } //index of the element in the structure
        public string TypeName { get { return "Finite Element"; } }
        public string Name { get; set; } = "General Element";
        public Line Line { get; set; } = new Line(); // the line with a current length in the current state
        public List<int> EndNodes { get; set; } = new List<int>(); //index of the end nodes of the element
        public double FreeLength { get; set; } = -1.0; // [m] - the Free length of the element
        public virtual ICrossSection CS { get; set; } = new CS_Circular(); //used for calculating volume and displaying the Element in GH. 
        public virtual BilinearMaterial Material { get; set; } = new BilinearMaterial(); //used for calculating mass and strength

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
        public Vector3d Weight { get { return MuscleAppConfig.g * Mass; } } //N

        public bool IsValid
        {
            get
            {
                if (CS.IsValid 
                && Material.IsValid 
                && Line.IsValid 
                && Strength.T1>=0 
                && Strength.T0 <=0
                && !(Strength.T0 == 0.0 && Strength.T1 == 0.0)
                ) return true;
                else return false;
            }
        }

        public double Tension { get; set; } //[N]



        ///// Strength /////

        public string BucklingLaw { get; set; } = "Yielding";
        public double kb { get; set; } = 1.0; //buckling factor
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
        public Interval Strength
        {
            get
            {
                return new Interval(Fyb, Material.Fyt);
            }
        }
        public Interval Resistance
        {
            get
            {
                double Fyt = Strength.T1;
                double Fyb = Strength.T0;
                return new Interval(Fyb * CS.Area, Fyt * CS.Area);
            }
        }
        public int Type // -1 if compression only element, 0 if withstand both, 1 if tension only element.
        { 
            get
            {
                double Fyt = Strength.T1; // strength in tension
                double Fyb = Strength.T0; // strength in compression
                if (Fyb < 0 && Fyt > 0) return 0; // Element withstands compression and tension -> Type = 0
                if (Fyt <= 0) return -1; // if strength in tension is null or invalid, Element withstands compression only -> Type = -1
                if (Fyb >= 0) return 1; // if strength in compression is null or invalid, Element withstands tension only -> Type = 1
                else return 0; 
            }
        } 

        public double UC
        {
            get
            {
                try
                {
                    if (Tension >= 0) return Tension / Resistance.T1;
                    else return Tension / Resistance.T0;
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

        public Element(Line aLine, ICrossSection aCS, BilinearMaterial aMat, string name, string buckling_law, double buckling_factor)
        {
            Init();
            Line = aLine;
            FreeLength = aLine.Length; // Use the length of the inputted line as the free length
            CS = aCS.Copy();
            Material = aMat.Copy();
            Name = name;
            BucklingLaw = buckling_law;
            kb = buckling_factor;
            if (kb <= 0) kb = 0;
        }


        public Element(Element other) // Copy constructor. This allows to create a new Element and modify it, without alterating the original
        {
            Name = other.Name;
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
            return $"{Name} {Idx} with free length {FreeLength:F3}m and mass {Mass:F1}kg.\n    In Compression : A={CS.Area * 1e6:F0}mm^2, E={Material.Ec * 1e-6:F0}MPa.\n   In Tension : A={CS.Area * 1e6:F0}mm^2, E={Material.Et * 1e-6:F0}MPa.";
        }




        #endregion Methods

    }
}