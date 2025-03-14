using System;
using Rhino.Geometry;

namespace MuscleApp.ViewModel
{
    public class BilinearMaterial
    {

        #region Properties
        /// <summary>
        /// Material name.
        /// </summary>
        public string Name { set; get; }

        /// <summary>
        /// compressive yield strength in N/m^2, must be negative.
        /// </summary>
        public double Fyc { 
            get
            {
                return LinearElasticDomain.T0;
            }
        }

        /// <summary>
        /// tensile yield strength in N/m^2.
        /// </summary>
        public double Fyt { 
            get
            {
                return LinearElasticDomain.T1;
            }
        }

        /// <summary>
        /// Material linear elastic domain [Fyc, Fyt] in N/m^2.
        /// where Fyc is the compressive yield strength and Fyt is the tensile yield strength.
        /// </summary>
        public Interval LinearElasticDomain { get; set; }

        /// <summary>
        /// Compressive Young modulus in N/m^2.
        /// </summary>
        public double Ec { set; get; }

        /// <summary>
        /// Tensile Young modulus in N/m^2.
        /// </summary>
        public double Et { set; get; }
        
        /// <summary>
        /// Material density in kg/m^3.
        /// </summary>
        public double Rho { set; get; }

        public bool IsValid
        {
            get
            {
                if (Fyc <= 0.0 
                && Fyt >= 0.0 
                && Ec >= 0.0 
                && Et >= 0.0 
                && !(Ec == 0.0 && Et == 0.0) // young moduli cannot be both 0 
                && Rho >= 0.0)
                {
                    return true;
                }

                return false;
            }
        }

        /// <summary>
        /// Property to set and get material thermic dilatation coefficient in (mm/mm)/°C.
        /// It is currently unsuported So its access modifier is set to private.
        /// </summary>
        private double Alpha { set; get; }

        #endregion Properties

        #region Constructors

        public BilinearMaterial()
        {
            Name = "Null Material";
            LinearElasticDomain = new Interval(double.NegativeInfinity, double.PositiveInfinity);
            Ec = 0.0; 
            Et = 0.0;
            Rho = 0.0;
        }

        /// <summary>
        /// Complete constructor allowing to define name and properties of the material.
        /// </summary>
        /// <param name="aName">Name of the material</param>
        /// <param name="aE">Young modulus of the material in N/m^2</param>
        /// <param name="aFy">Yield strengh of the material in N/m^2</param>
        /// <param name="aRho">Density of the material in kg/m^3</param>
        public BilinearMaterial(string aName, double aEc, double aEt, double aFyc, double aFyt, double aRho)
        {
            Name = aName;
            Ec = aEc;     // N/m^2
            Et = aEt;     // N/m^2
            LinearElasticDomain = new Interval(aFyc, aFyt); // N/m^2

            Rho = aRho;         // kg/m^3
            Alpha = 0.0;
        }

        public BilinearMaterial(string aName, double aEc, double aEt, Interval interval, double aRho)
        {
            Name = aName;
            Ec = aEc;     // N/m^2
            Et = aEt;     // N/m^2
            LinearElasticDomain = interval; // N/m^2
            Rho = aRho;         // kg/m^3
            Alpha = 0.0;
        }


        /// <summary>
        /// Copy constructor.
        /// </summary>
        /// <param name="aMaterial">Material to copy</param>
        public BilinearMaterial(BilinearMaterial aMaterial)
        {
            Name = aMaterial.Name;
            LinearElasticDomain = aMaterial.LinearElasticDomain;
            Ec = aMaterial.Ec;     // N/m^2
            Et = aMaterial.Et;     // N/m^2
            Rho = aMaterial.Rho;         // kg/m^3

            Alpha = aMaterial.Alpha;
        }

        public BilinearMaterial Copy()
        {
            return new BilinearMaterial(this);
        }
        #endregion Constructors

        #region Methods



        /// <summary>
        /// Return human readable string descibing the material.
        /// </summary>
        /// <returns>Humain readable description of the material.</returns>
        /// <example>
        /// >> Material m = new Material("S235 Steel", 235.0 * 1e6, 210.0 * 1e9, 7850);
        /// >> Console.WriteLine(m);
        /// >> "S235 Steel -- ρ: 7850kg/m^3
        ///     in compression, fy: 235Mpa - E: 210000MPa
        ///     in tension, fy: 235Mpa - E: 210000MPa"
        /// </example>
        public override string ToString()
        {
            return $"{Name} -- \u03c1: {Rho:F0}kg/m^3 \n in compression, fy: {Fyc * 1e-6:F2}MPa - E: {Ec * 1e-6:F2}MPa \n in tension, fy: {Fyt * 1e-6:F2}MPa - E: {Et * 1e-6:F2}MPa";
        }

        #endregion Methods

    }
}