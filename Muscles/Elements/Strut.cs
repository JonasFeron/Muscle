using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using Muscles.CrossSections;
using Muscles.Materials;
using System.Collections.Generic;
using Muscles.Elements;

namespace Muscles.Elements
{
    /// <summary>
    /// A Strut is a linear elastic structural element working only in compression. a Strut may or may not be sensitive to buckling.
    /// </summary>
    public class Strut : Element
    {

        #region Properties
        public override string TypeName { get { return "Strut"; } }

        public override Interval Stress_Allowable
        {
            get
            {
                return new Interval(-Stress_buckling, 0);
            }
        }


        #endregion Properties

        #region Constructors

        public Strut(): base()
        {
        }

        public Strut(Line aLine, ICrossSection aCS, Muscles_Material aMat, string law, double k)
            : base(aLine,aCS,aCS,aMat,aMat,law,k)
        {
            ICrossSection CS_No_Tension = new CS_Circular(); //create a cross section with null Area
            Muscles_Material Mat_No_Tension = new Muscles_Material(); //create a material with null E and Rho
            CS_Tens = CS_No_Tension;
            Mat_Tens = Mat_No_Tension;
        }

        public Strut(Strut other) : base(other)
        {

        }

        #endregion Constructors

        #region Methods

        public override Element Duplicate()
        {
            return new Strut(this);
        }

        public override string ToString()
        {
            return $"Strut {Ind} is {Length0:F3}m and {Mass:F1}kg.\n   In Compression : A={CS_Comp.Area * 1e6:F0}mm^2, E={Mat_Comp.E * 1e-6:F0}MPa. No Tension.";
        }

        #endregion Methods

    }
}