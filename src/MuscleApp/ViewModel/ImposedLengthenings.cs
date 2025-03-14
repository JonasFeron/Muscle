using System;
using System.Collections.Generic;
using System.Linq;
using Rhino.Geometry;

namespace Muscle.ViewModel
{
    public class ImposedLenghtenings
    {

        #region Properties

        public Element Element { get; set; }
        public double Value { get; set; } //(m)  The length variation (+ for lengthening) to apply on the element of the structure

        public double AsTension
        {
            get
            {
                double A = Element.CS.Area; //[m2]
                double E = Element.Material.E; //[N/m2]
                double LFree = Element.FreeLength + Value; //[m]
                double P = E * A * Value / LFree; //[N] positive for lengthenings, negative for shortenings
                return -P;
            }
        }

        public PointLoad AsPointLoad0
        {
            get
            {

                Vector3d Load = 1 * Element.Line.UnitTangent * AsTension;
                return new PointLoad(Element.Line.From, Load);
            }
        }
        public PointLoad AsPointLoad1
        {
            get
            {
                Vector3d Load = -1 * Element.Line.UnitTangent * AsTension;
                return new PointLoad(Element.Line.To, Load);
            }
        }
        public bool IsValid { get { return Element != null && Value != 0.0; } }


        #endregion Properties
        #region Constructors

        public ImposedLenghtenings()
        {
            Element = new Element();
            Value = 0.0;
        }
        public ImposedLenghtenings(Element e)
        {
            Element = e;
            Value = 0.0;
        }
        public ImposedLenghtenings(Element e, double DL)
        {
            Element = e;
            Value = DL;
        }

        public ImposedLenghtenings(ImposedLenghtenings other)
        {
            Element = other.Element;
            Value = other.Value;
        }
        #endregion Constructors


        #region Methods
        public ImposedLenghtenings Duplicate()
        {
            return new ImposedLenghtenings(this);
        }
        public override string ToString()
        {
            if (Value >= 0) return $"Lengthening of {Value * 1e3:F3}mm in Element {Element.Name}{Element.Idx} whose initial free length is {Element.FreeLength * 1e3:F3}mm.";
            else return $"Shortening of {Value * 1e3:F3}mm in Element {Element.Name}{Element.Idx} whose initial free length is {Element.FreeLength * 1e3:F3}mm.";

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
        public double Tension2Lengthening(double tension)
        {
            double A = Element.CS.Area; //[m2]
            double E = Element.Material.E; //[N/m2]
            double LFreeInit = Element.FreeLength; //[m]
            double LFreeFinal = LFreeInit / (1 + tension / (E * A)); //[m]
            double DL = LFreeFinal - LFreeInit;
            return DL;
        }

        #endregion Methods

    }



}
