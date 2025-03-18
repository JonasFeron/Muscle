using System;
using System.Collections.Generic;
using System.Linq;
using Rhino.Geometry;
using MuscleCore.FEModel;
using MuscleCore.Converters;

namespace MuscleApp.ViewModel
{
    public class Prestress
    {
        #region Properties

        public Element Element { get; set; }
        public double Value { get; set; } //(m)  The length variation (+ for lengthening) to apply on the element of the structure
        
        public double EquivalentTension // for visualisation purpose only. 
        {
            get
            {
                if (Element == null)
                    return 0.0;
                
                // Get the element's properties
                double area = Element.CS.Area; // [m²]
                double young;

                // Determine which Young's modulus to use based on the current state
                if (Math.Abs(Element.Tension) < 1e-10) // If tension is close to zero
                    young = Math.Max(Element.Material.Ec, Element.Material.Et); // Use the maximum of Ec and Et
                else if (Element.Tension < 0) // if Element is in compression
                    young = Element.Material.Ec; // [N/m²]
                else // if Element is in tension
                    young = Element.Material.Et; // [N/m²]
                
                // Calculate the new free length (original + variation)
                double newFreeLength = Element.FreeLength + Value; // [m]

                if (Math.Abs(newFreeLength) < 1e-10) // newFreeLength = 0 
                    return 0.0;
                
                double equivalentTension = young * area * (-Value) / newFreeLength; // [N] A lengthening (+) creates a compression force (-)
                
                return equivalentTension;
            }
        }

        public PointLoad EquivalentPointLoad0 // for visualisation purpose only. 
        {
            get
            {
                Vector3d Load = 1 * Element.Line.UnitTangent * EquivalentTension;
                return new PointLoad(Element.Line.From, Load);
            }
        }
        
        public PointLoad EquivalentPointLoad1 // for visualisation purpose only. 
        {
            get
            {
                Vector3d Load = -1 * Element.Line.UnitTangent * EquivalentTension;
                return new PointLoad(Element.Line.To, Load);
            }
        }
        
        public bool IsValid { get { return Element != null && Value != 0.0; } }

        #endregion Properties
        
        #region Constructors

        public Prestress()
        {
            Element = new Element();
            Value = 0.0;
        }
        
        public Prestress(Element e)
        {
            Element = e;
            Value = 0.0;
        }
        
        public Prestress(Element e, double DL)
        {
            Element = e;
            Value = DL;
        }

        public Prestress(Prestress other)
        {
            Element = other.Element;
            Value = other.Value;
        }
        
        #endregion Constructors

        #region Methods
        
        
        public Prestress Duplicate()
        {
            return new Prestress(this);
        }
        
        public override string ToString()
        {
            if (Value >= 0) 
                return $"Lengthening of {Value * 1e3:F3}mm in Element {Element.Name}{Element.Idx} whose initial free length is {Element.FreeLength * 1e3:F3}mm.";
            else 
                return $"Shortening of {Value * 1e3:F3}mm in Element {Element.Name}{Element.Idx} whose initial free length is {Element.FreeLength * 1e3:F3}mm.";
        }

        //public double Tension2Lengthening(double tension)
        //{
        //    double A = Element.CS.Area; //[m2]
        //    double E = Element.Material.E; //[N/m2]
        //    double LFreeInit = Element.FreeLength; //[m]
        //    double LFreeFinal = LFreeInit / (1 + tension / (E * A)); //[m]
        //    double DL = LFreeFinal - LFreeInit;
        //    return DL;
        //}

        #endregion Methods
    }
}
