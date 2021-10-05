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
        public double Value { get; set; } //(N)  Initial force in the element when considering that all nodes of the structure are blocked. Once the nodes are realeased this prestress force may spread in the structure. 
        public PointLoad AsPointLoad0
        {
            get
            {
                Vector3d Load = Element.Line.UnitTangent * Value;
                return new PointLoad(Element.Line.From, Load);
            }
        }
        public PointLoad AsPointLoad1
        {
            get
            {
                Vector3d Load = -1 * Element.Line.UnitTangent * Value;
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
        public PrestressLoad(Element e,double P_value)
        {
            Element = e;
            Value = P_value;
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
            return $"Prestress of {Value/1e3:F3}kN in Element {Element.Ind}.";
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