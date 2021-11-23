using System;
using System.Collections.Generic;
using System.Linq;
using Muscles.Elements;
using Muscles.Loads;
using Rhino.Geometry;

namespace Muscles.Loads
{
    public class PrestressLoad
    {

        #region Properties

        public Element Element { get; set; }
        public double Value { get; set; } //(m)  The lengthening to apply on the element of the structure
        public PointLoad AsPointLoad0
        {
            get
            {
                double A = Element.CS_Main.Area; //[m2]
                double E = Element.Mat_Main.E; //[N/m2]
                double LFree = Element.LFree + Value; //[m]
                double P = E * A * Value / LFree; //[N] positive for lengthenings, negative for shortenings
                Vector3d Load = -1*Element.Line.UnitTangent * P;
                return new PointLoad(Element.Line.From, Load);
            }
        }
        public PointLoad AsPointLoad1
        {
            get
            {
                double A = Element.CS_Main.Area; //[m2]
                double E = Element.Mat_Main.E; //[N/m2]
                double LFree = Element.LFree + Value; //[m]
                double P = E * A * Value / LFree; //[N] positive for lengthenings, negative for shortenings
                Vector3d Load = Element.Line.UnitTangent * P;
                return new PointLoad(Element.Line.To, Load);
            }
        }
        public bool IsValid { get { return Element != null && Value != 0.0;} }


        #endregion Properties
        #region Constructors

        public PrestressLoad()
        {
            Element = new Element();
            Value = 0.0;
        }
        public PrestressLoad(Element e,double DL)
        {
            Element = e;
            Value = DL;
        }

        public PrestressLoad(PrestressLoad other)
        {
            Element = other.Element;
            Value = other.Value;
        }
        #endregion Constructors


        #region Methods
        public PrestressLoad Duplicate()
        {
            return new PrestressLoad(this);
        }
        public override string ToString()
        {
            if (Value >=0) return $"Lengthening of {Value * 1e3:F3}mm in Element {Element.TypeName}{Element.Ind} whose initial free length is {Element.LFree * 1e3:F3}mm.";
            else return $"Shortening of {Value * 1e3:F3}mm in Element {Element.TypeName}{Element.Ind} whose initial free length is {Element.LFree * 1e3:F3}mm.";

        }

        //public static InitialForce Merge(InitialForce P1, InitialForce P2)
        //{
        //    InitialForce MergedForces = P1.Duplicate();
        //    if (P1.Element.Id == P2.Element.Id)
        //    {
        //        MergedForces.InitialForce_as_Load += P2.InitialForce_as_Load;
        //    }
        //    return MergedForces;
        //}

        #endregion Methods

    }



}