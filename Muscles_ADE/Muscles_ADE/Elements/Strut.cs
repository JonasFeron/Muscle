using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using Muscles_ADE.CrossSections;
using Muscles_ADE.Materials;
using System.Collections.Generic;
using Muscles_ADE.Elements;
using System;

namespace Muscles_ADE.Elements
{
    /// <summary>
    /// A Strut is a linear elastic structural element working only in compression. a Strut may or may not be sensitive to buckling.
    /// </summary>
    public class Strut : Element
    {

        #region Properties
        public override string TypeName { get { return "Strut"; } }
        public override int Type { get { return -1; } }


        public bool CanResistTension { get; set; } //if true, Tension will be allowed in the finite element analysis. If false, run a non-linear analysis with 0 forces in the cracked strut.

        public override ICrossSection CS_Main
        {
            get
            {
                return CS_Comp;
            }
        }
        public override ICrossSection CS_Tens
        {
            get
            {
                if (CanResistTension) return CS_Comp;
                else return new CS_Circular();//create a cross section with null Area
            }
        }
        public override Muscles_Material Mat_Main
        {
            get
            {
                return Mat_Comp;
            }
        }
        public override Muscles_Material Mat_Tens
        {
            get
            {
                if (CanResistTension) return Mat_Comp;
                else return new Muscles_Material();//create a material with null E,Fy and Rho
            }
        }

        public override double UC // the unity check should always be between 0 and 1. otherwise element is not valid. 
        {
            get
            {
                try
                {
                    return Tension / AllowableTension.T0; // AllowableTension.T0 is <=0. Thus this expression returns negative unity check for struts in Tension
                }
                catch (DivideByZeroException)
                {
                    if (Tension >= 0) return double.NegativeInfinity;
                    else return double.PositiveInfinity;
                }
            }
        }


        #endregion Properties

        #region Constructors

        public Strut() : base()
        {
        }

        public Strut(Line aLine, double lFree, ICrossSection aCS, Muscles_Material aMat, string law, double k, bool canResistTension)
            : base(aLine, lFree, aCS, aCS, aMat, aMat, law, k)
        {
            CanResistTension = canResistTension;
        }

        public Strut(Strut other) : base(other)
        {
            CanResistTension = other.CanResistTension;
        }

        #endregion Constructors

        #region Methods

        public override Element Duplicate()
        {
            return new Strut(this);
        }

        //public override string ToString()
        //{
        //    return $"Strut {Ind} is {LFree:F3}m and {Mass:F1}kg.\n   In Compression : A={CS_Comp.Area * 1e6:F0}mm^2, E={Mat_Comp.E * 1e-6:F0}MPa. No Tension.";
        //}

        #endregion Methods

    }
}