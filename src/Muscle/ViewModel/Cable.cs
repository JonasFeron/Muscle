using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using System.Collections.Generic;
using System;

namespace Muscle.ViewModel
{
    /// <summary>
    /// A Cable is a linear elastic structural element working only in Tension.
    /// </summary>
    public class Cable : Element
    {

        #region Properties
        public override string TypeName { get { return "Cable"; } }
        public override int Type { get { return 1; } }

        public bool CanResistCompression { get; set; } //if true, compression will be allowed in the finite element analysis. If false, run a non-linear analysis with 0 forces in the slack cables.

        public override ICrossSection CS_Main
        {
            get
            {
                return CS_Tens;
            }
        }
        public override ICrossSection CS_Comp
        {
            get
            {
                if (CanResistCompression) return CS_Tens;
                else return new CS_Circular();//create a cross section with null Area
            }
        }
        public override Muscles_Material Mat_Main
        {
            get
            {
                return Mat_Tens;
            }
        }
        public override Muscles_Material Mat_Comp
        {
            get
            {
                if (CanResistCompression) return Mat_Tens;
                else return new Muscles_Material();//create a material with null E,Fy and Rho
            }
        }

        public override Interval AllowableStress
        {
            get
            {
                return new Interval(-Mat_Comp.Fy, Mat_Tens.Fy);
            }
        }
        public override double UC // the unity check should always be between 0 and 1. otherwise element is not valid. 
        {
            get
            {
                try
                {
                    return Tension / AllowableTension.T1; // for cable in compression return negative unity check 
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

        public Cable() : base()
        {
        }

        public Cable(Line aLine, double lFree, ICrossSection aCS, Muscles_Material aMat, bool canResistCompression)
            : base(aLine, lFree, aCS, aCS, aMat, aMat, "Not Applicable", 1.0)
        {
            CanResistCompression = canResistCompression;
        }

        public Cable(Cable other) : base(other)
        {
            CanResistCompression = other.CanResistCompression;
        }

        #endregion Constructors

        #region Methods

        public override Element Duplicate()
        {
            return new Cable(this);
        }

        //public override string ToString()
        //{
        //    //return $"Cable {Ind} is {LFree:F3}m and {Mass:F1}kg.\n   In Tension : A={CS_Tens.Area * 1e6:F0}mm^2, E={Mat_Tens.E * 1e-6:F0}MPa. No Compression.";
        //    return $"Cable {Ind} with free length {LFree:F3}m and mass {Mass:F1}kg.\n    In Compression : A={CS_Comp.Area * 1e6:F0}mm^2, E={Mat_Comp.E * 1e-6:F0}MPa.\n   In Tension : A={CS_Tens.Area * 1e6:F0}mm^2, E={Mat_Tens.E * 1e-6:F0}MPa.";
        //}

        #endregion Methods

    }
}
