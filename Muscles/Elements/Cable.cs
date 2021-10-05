using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using Muscles.CrossSections;
using Muscles.Materials;
using System.Collections.Generic;
using Muscles.Elements;

namespace Muscles.Elements
{
    /// <summary>
    /// A Cable is a linear elastic structural element working only in tension.
    /// </summary>
    public class Cable : Element
    {

        #region Properties
        public override string TypeName { get { return "Cable"; } }

        public override Interval Stress_Allowable
        {
            get
            {
                return new Interval(0, Mat_Tens.Fy);
            }
        }

        #endregion Properties

        #region Constructors

        public Cable(): base()
        {
        }

        public Cable(Line aLine, ICrossSection aCS, Muscles_Material aMat)
            : base(aLine,aCS,aCS,aMat,aMat,"Not Applicable",1.0)
        {
            ICrossSection CS_No_Comp = new CS_Circular(); //create a cross section with null Area
            Muscles_Material Mat_No_Comp = new Muscles_Material(); //create a material with null E and Rho
            CS_Comp = CS_No_Comp;
            Mat_Comp = Mat_No_Comp;
            CS_Main = CS_Tens;
            Mat_Main = Mat_Tens;
        }

        public Cable(Cable other):base(other)
        {

        }

        #endregion Constructors

        #region Methods

        public override Element Duplicate()
        {
            return new Cable(this);
        }

        public override string ToString()
        {
            return $"Cable {Ind} is {Length0:F3}m and {Mass:F1}kg.\n   In Tension : A={CS_Tens.Area * 1e6:F0}mm^2, E={Mat_Tens.E * 1e-6:F0}MPa. No Compression.";
        }

        #endregion Methods

    }
}