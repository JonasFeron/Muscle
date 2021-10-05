using Rhino.Geometry;
using Grasshopper.Kernel.Types;
using Muscles.CrossSections;
using Muscles.Materials;
using System.Collections.Generic;

namespace Muscles.Elements
{
    /// <summary>
    /// A Bar is a linear elastic structural element working both in tension and compression with the same stiffness. In compression, a bar may or may not be sensitive to buckling.
    /// </summary>
    public class Bar : Element
    {

        #region Properties
        public override string TypeName { get { return "Bar"; } }


        #endregion Properties

        #region Constructors

        public Bar(): base()
        {
        }

        public Bar(Line aLine, ICrossSection aCS, Muscles_Material aMat, string law, double k)
            : base(aLine,aCS,aCS,aMat,aMat,law, k)
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

        public override string ToString()
        {
            return $"Bar {Ind} is {Length0:F3}m and {Mass:F1}kg.\n   In Tension & Compression : A={CS_Comp.Area * 1e6:F0}mm^2, E={Mat_Comp.E * 1e-6:F0}MPa.";
        }

        #endregion Methods

    }
}