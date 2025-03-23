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
        public double FreeLengthVariation { get; set; } //(m)  The length variation (+ for lengthening) to apply on the element of the structure
        
        public double EquivalentTension // for visualisation purpose only. 
        {
            get
            {
                if (Element == null)
                    return 0.0;
                
                double k_modified = ModifiedAxialStiffness(); // [N/m]
                
                double equivalentTension = k_modified * (-FreeLengthVariation); // [N] A lengthening (+) creates a compression force (-)
                
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
        
        public bool IsValid { get { return Element != null && FreeLengthVariation != 0.0; } }

        #endregion Properties
        
        #region Constructors

        public Prestress()
        {
            Element = new Element();
            FreeLengthVariation = 0.0;
        }
        
        public Prestress(Element e)
        {
            Element = e;
            FreeLengthVariation = 0.0;
        }
        
        /// <summary>
        /// Constructor for prestress calculation based on direct free length variation.
        /// </summary>
        /// <param name="e">The element to apply prestress to</param>
        /// <param name="freeLengthVariation">The free length variation [m]</param>
        public Prestress(Element e, double freeLengthVariation)
        {
            Element = e;
            FreeLengthVariation = freeLengthVariation;
        }

        public Prestress(Prestress other)
        {
            Element = other.Element;
            FreeLengthVariation = other.FreeLengthVariation;
        }
        
        #endregion Constructors

        #region Methods
        
        /// <summary>
        /// Duplicate the prestress object.
        /// </summary>
        /// <returns>A duplicate of the prestress object.</returns>
        public Prestress Duplicate()
        {
            return new Prestress(this);
        }
        
        public override string ToString()
        {
            if (FreeLengthVariation >= 0) 
                return $"Lengthening of {FreeLengthVariation * 1e3:F3}mm in Element {Element.Name}{Element.Idx} whose initial free length is {Element.FreeLength * 1e3:F3}mm.";
            else 
                return $"Shortening of {FreeLengthVariation * 1e3:F3}mm in Element {Element.Name}{Element.Idx} whose initial free length is {Element.FreeLength * 1e3:F3}mm.";
        }

        /// <summary>
        /// Determines the appropriate Young's modulus to use based on the current state of elastic elongation.
        /// </summary>
        /// <param name="element">The element to evaluate</param>
        /// <param name="elasticElongation">The elastic elongation to evaluate.</param>
        /// <returns>The Young's modulus [N/m²] based on whether the element is in tension, compression, or near zero tension.</returns>
        private static double CurrentYoungModulus(Element element, double elasticElongation)
        {         
            if (Math.Abs(elasticElongation) < 1e-10) // If tension is close to zero
                return Math.Max(element.Material.Ec, element.Material.Et); // Use the maximum of Ec and Et
            else if (elasticElongation < 0) // if Element is in compression
                return element.Material.Ec; // [N/m²]
            else // if Element is in tension
                return element.Material.Et; // [N/m²]
        }

        /// <summary>
        /// Determines the appropriate Young's modulus to use based on the current state of elastic elongation.
        /// </summary>
        /// <param name="elasticElongation">The elastic elongation to evaluate.</param>
        /// <returns>The Young's modulus [N/m²] based on whether the element is in tension, compression, or near zero tension.</returns>
        private double CurrentYoungModulus(double elasticElongation)
        {         
            return CurrentYoungModulus(Element, elasticElongation);
        }
        
        /// <summary>
        /// Calculates the modified axial stiffness of the element given the prestress variation.
        /// The modified axial stiffness is the product of the Young's modulus and the cross-sectional area divided by the modified free length.
        /// </summary>
        /// <returns>The modified axial stiffness [N/m] of the element.</returns>
        private double ModifiedAxialStiffness()
        {         
                // Get the element's properties
                double area = Element.CS.Area; // [m²]
                double young = CurrentYoungModulus(Element.Line.Length - Element.FreeLength); //Young's modulus [N/m²], based on current elastic elongation
                
                // Calculate the new free length (original + variation)
                double newFreeLength = Element.FreeLength + FreeLengthVariation; // [m]

                if (Math.Abs(newFreeLength) < 1e-10) // newFreeLength = 0 
                    return double.PositiveInfinity;
                
                double modifiedAxialStiffness = young * area / newFreeLength; // [N/m]
                return modifiedAxialStiffness;
        }
        #endregion Methods

        /// <summary>
        /// Creates a prestress object based on desired tension.
        /// Calculates the required free length variation (dl0) to achieve a specified tension.
        /// </summary>
        /// <param name="e">The element to apply prestress to</param>
        /// <param name="targetTension">The desired tension force [N]</param>
        /// <returns>A new Prestress object with the calculated free length variation</returns>
        /// <remarks>
        /// Uses the relationship: tension = EA/(l0 + dl0) * dl0
        /// Solving for dl0: dl0 = l0 / (EA/tension - 1)
        /// </remarks>
        public static Prestress FromTension(Element e, double targetTension)
        {
            // Get element properties
            double A = e.CS.Area; // [m²]
            double currentLength = e.Line.Length; // [m]
            double freeLength = e.FreeLength; // [m]
            double E = CurrentYoungModulus(e, currentLength - freeLength); // [N/m²]
            
            // Calculate free length variation using optimized formula
            double freeLengthVariation = freeLength / (E * A / targetTension - 1);
            
            return new Prestress(e, freeLengthVariation);
        }
    }
}
