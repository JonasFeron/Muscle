using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using Muscles.CrossSections;
using Muscles.Materials;
using System.Collections.Generic;

namespace Muscles.Elements
{
    /// <summary>
    /// A Bar is a linear elastic structural element working both in Tension and compression with the same stiffness. In compression, a bar may or may not be sensitive to buckling.
    /// </summary>
    public class Bar : Element
    {

        #region Properties
        public override string TypeName { get { return "Bar"; } }
        public override int Type { get { return -1; } }



        #endregion Properties

        #region Constructors

        public Bar(): base()
        {
        }

        public Bar(Line aLine,double lFree, ICrossSection aCS, Muscles_Material aMat, string law, double k)
            : base(aLine,lFree,aCS,aCS,aMat,aMat,law, k)
        {
        }

        public Bar(Bar other) : base(other)
        {

        }

        #endregion Constructors

        #region Methods

        public override Element Duplicate()
        {
            return new Bar(this);
        }

        //public override string ToString()
        //{
        //    //return $"Bar {Ind} is {LFree:F3}m and {Mass:F1}kg.\n   In Tension & Compression : A={CS_Comp.Area * 1e6:F0}mm^2, E={Mat_Comp.E * 1e-6:F0}MPa.";
        //    return $"Bar {Ind} with free length {LFree:F3}m and mass {Mass:F1}kg.\n    In Compression : A={CS_Comp.Area * 1e6:F0}mm^2, E={Mat_Comp.E * 1e-6:F0}MPa.\n   In Tension : A={CS_Tens.Area * 1e6:F0}mm^2, E={Mat_Tens.E * 1e-6:F0}MPa.";
        //}

        #endregion Methods

    }
}