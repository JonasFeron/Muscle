using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using Muscles.CrossSections;
using Muscles.Materials;
using System.Collections.Generic;
using System.Threading;
using Muscles.Loads;
using System;

namespace Muscles.Elements
{
    /// <summary>
    /// An Element is the most general (bi-)linear elastic structural element. It allows modelling linear reinforced concrete element. In tension, the rebars (A_tens, E_tens) are working. In compression, the concrete (A_comp, E_comp) is working. In compression, the element may or may not be sensitive to buckling. The mass is obtained by considering only the compressive cross-section and material. 
    /// </summary>
    public class Element
    {
        #region Properties
        public int Ind { get; set; } //index of the element in the structure
        public virtual string TypeName { get { return "General Element"; } }
        public Line Line { get; set; }
        public List<int> ExtremitiesIndex { get; set; }
        public double Length0 { get; set; }
        public ICrossSection CS_Tens { get; set; } //participate to the stiffness in tension
        public ICrossSection CS_Comp { get; set; } //participate to the stiffness in compression
        public Muscles_Material Mat_Tens { get; set; } //participate to the stiffness in tension
        public Muscles_Material Mat_Comp { get; set; } //participate to the stiffness in compression

        public ICrossSection CS_Main { get; set; } //used for calculating volume and displaying the Element in GH. 
        public Muscles_Material Mat_Main { get; set; } //used for calculating mass

        public double V //m3
        {
            get 
            {
                return Length0 * CS_Main.Area;
            } 
        }  
        public double Mass//kg
        {
            get
            { 
                return V * Mat_Main.Rho;
            }
        }
        public Vector3d Weight{ get { return (AccessToAll.g * Mass); } } //N

        public bool IsValid
        {
            get
            {
                if (CS_Main.IsValid && Mat_Main.IsValid && Line.IsValid && AxialForce_Current >= AxialForce_Allowable.T0 && AxialForce_Current<=AxialForce_Allowable.T1) return true;
                else return false;
            }
        }

        ///// Acting forces /////

        public double AxialForce_Already_Applied { get; set; } //(N)  Initial force in the element in equilibrium in the structure (with or without external load)
        public double AxialForce_To_Apply { get; set; } //(N)  Initial force in the element when considering that all nodes of the structure are blocked. Once the nodes are realeased this prestress force may spread in the structure.
        //public PointLoad PrestressLoad0
        //{
        //    get
        //    {
        //        Vector3d Load = Line.UnitTangent * AxialForce_To_Apply;
        //        return new PointLoad(Line.From, Load);
        //    }
        //}
        //public PointLoad PrestressLoad1
        //{
        //    get
        //    {
        //        Vector3d Load = -1 * Line.UnitTangent * AxialForce_To_Apply;
        //        return new PointLoad(Line.To, Load);
        //    }
        //}
        public List<double> AxialForce_Results{ get; set; }
        public List<double> AxialForce_Total { get; set; }
        public double AxialForce_Current 
        { 
            get
            {
                int final = AxialForce_Total.Count - 1;
                if (final >= 0) return AxialForce_Total[final];
                else return 0.0;
            }    
        }

        //public double Stress_Already_Applied
        //{   
        //    get
        //    {
        //        if (AxialForce_Already_Applied>=0) return AxialForce_Already_Applied/CS_Tens.Area;
        //        else return AxialForce_Already_Applied / CS_Comp.Area;
        //    }        
        //}

        ///// Resisting forces /////

        public string Buckling_Law { get; set; }
        public double kb { get; set; } //buckling factor
        public double Lambda
        {
            get
            {
                double Lb = kb * Length0; // buckling length [m]
                double A = CS_Comp.Area;
                double I = CS_Comp.Inertia;
                return Lb * Math.Sqrt(A / I);
            }
        }
        public double Lambda_E
        {
            get
            {
                double E = Mat_Comp.E;
                double Fy = Mat_Comp.Fy;
                return Math.PI * Math.Sqrt(E / Fy);
            }
        }

        public double Lambda_Adim
        {
            get
            {
                return Lambda/Lambda_E;
            }
        }

        private double Alpha //imperfection factor of buckling law
        {
            get
            {
                switch (Buckling_Law)
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
                return 0.5 * (1 + Alpha * (Lambda_Adim - 0.2) + Math.Pow(Lambda_Adim,2));
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
                switch (Buckling_Law)
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
                }
                return 1.0; // return yielding in all other cases !
            }
        }
        protected double Stress_buckling 
        { 
            get
            {
                double Fy = Mat_Comp.Fy;
                return Xsi * Fy;
            }
        }
        public virtual Interval Stress_Allowable
        {
            get
            {
                return new Interval(-Stress_buckling, Mat_Tens.Fy);
            }
        }
        public Interval AxialForce_Allowable
        {
            get
            {
                double S_Tens = Stress_Allowable.T1;
                double S_Comp = Stress_Allowable.T0;
                return new Interval(S_Comp*CS_Comp.Area, S_Tens * CS_Tens.Area);
            }
        }
        public double UC
        {
            get
            {
                try
                {
                    if (AxialForce_Current >= 0) return AxialForce_Current / AxialForce_Allowable.T1;
                    else return AxialForce_Current / AxialForce_Allowable.T0;
                }
                catch (DivideByZeroException)
                {
                    if (AxialForce_Current >= 0) return AxialForce_Current / AxialForce_Allowable.T0; // for strut in tension return negative unity check 
                    else return AxialForce_Current / AxialForce_Allowable.T1; // for cable in compression return negative unity check 
                }
            }
        }



        #endregion Properties

        #region Constructors
        private void Init()
        {
            Ind = -1;
            Line = new Line();
            Length0 = 0.0;
            ExtremitiesIndex = new List<int>();
            CS_Tens = new CS_Circular();
            CS_Comp = new CS_Circular();
            Mat_Tens = new Muscles_Material();
            Mat_Comp = new Muscles_Material();
            CS_Main = CS_Comp;
            Mat_Main = Mat_Comp;
            Buckling_Law = "yielding";
            kb = 1.0;
            
            AxialForce_Already_Applied = 0;
            AxialForce_To_Apply = 0;
            AxialForce_Results = new List<double>();
            AxialForce_Total = new List<double>();

        }


        public Element()
        {
            Init();
        }

        public Element(Line aLine, ICrossSection aCS_Comp, ICrossSection aCS_Tens, Muscles_Material aMat_Comp, Muscles_Material aMat_Tens,string buckling_law, double buckling_factor)
        {
            Init();
            Line = aLine;
            Length0 = aLine.Length;
            CS_Comp = aCS_Comp;
            CS_Tens = aCS_Tens;
            Mat_Comp = aMat_Comp;
            Mat_Tens = aMat_Tens;
            CS_Main = CS_Comp;
            Mat_Main = Mat_Comp;
            Buckling_Law = buckling_law;
            kb = buckling_factor;
            if (kb <= 0) kb = 0;

        }

        public Element(Element other) // Copy constructor. This allows to create a new Element and modify it, without alterating the original
        {
            Line = other.Line;
            Length0 = other.Length0;
            ExtremitiesIndex = other.ExtremitiesIndex;
            CS_Tens = other.CS_Tens.Duplicate();
            CS_Comp = other.CS_Comp.Duplicate();
            Mat_Tens = other.Mat_Tens.Duplicate();
            Mat_Comp = other.Mat_Comp.Duplicate();
            CS_Main = other.CS_Main.Duplicate();
            Mat_Main = other.Mat_Main.Duplicate();
            Buckling_Law = other.Buckling_Law;
            kb = other.kb;
            Ind = other.Ind;
            AxialForce_Already_Applied = other.AxialForce_Already_Applied;
            AxialForce_To_Apply = other.AxialForce_To_Apply;
            AxialForce_Results = other.AxialForce_Results;
            AxialForce_Total = other.AxialForce_Total;
        }

        #endregion Constructors

        #region Methods

        public virtual Element Duplicate()
        {
            return new Element(this);
        }

        public override string ToString()
        {
            //if (this is Cable) return (this as Cable).ToString();
            //if (this is Strut) return (this as Strut).ToString();
            //if (this is Bar) return (this as Bar).ToString();
            return $"Element {Ind} is {Length0:F3}m and {Mass:F1}kg.\n   In Tension : A={CS_Tens.Area * 1e6:F0}mm^2, E={Mat_Tens.E* 1e-6:F0}MPa.\n    In Compression : A={CS_Comp.Area * 1e6:F0}mm^2, E={Mat_Comp.E * 1e-6:F0}MPa.";
        }


        

        #endregion Methods

    }
}