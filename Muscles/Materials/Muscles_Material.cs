using System;

namespace Muscles.Materials
{
    public class Muscles_Material
    {

        #region Properties

        /// <summary>
        /// Material yield strength in N/m^2.
        /// </summary>
        public double Fy { set; get; }
        

        public bool IsValid
        {
            get
            {
                if (Fy < 0.0 || E < 0.0 || Rho < 0.0)
                {
                    return false;
                }

                return true;
            }
        }

        /// <summary>
        /// Material name.
        /// </summary>
        public string Name { set; get; }
        /// <summary>
        /// Material density in kg/m^3.
        /// </summary>
        public double Rho { set; get; }

        /// <summary>
        /// Material Young modulus in N/m^2.
        /// </summary>
        public double E { set; get; }

        /// <summary>
        /// Failure is true if stress is higher than Fy
        ///// </summary>
        //public bool Failure { set; get; }

        /// <summary>
        /// Property to set and get material thermic dilatation coefficient in (mm/mm)/°C.
        /// It is currently unsuported So its access modifier is set to private.
        /// </summary>
        private double Alpha { set; get; }

        #endregion Properties

        #region Constructors

        public Muscles_Material()
        {
            Name = "Null Material";
            Fy = 0.0;
            E = 0.0;
            Rho = 0.0;
        }

        /// <summary>
        /// Complete constructor allowing to define name and properties of the material.
        /// </summary>
        /// <param name="aName">Name of the material</param>
        /// <param name="aE">Young modulus of the material in N/m^2</param>
        /// <param name="aFy">Yield strengh of the material in N/m^2</param>
        /// <param name="aRho">Density of the material in kg/m^3</param>
        public Muscles_Material(string aName, double aE, double aFy, double aRho)
        {
            Name = aName;
            E = aE;     // N/m^2
            Fy = Math.Abs(aFy);           // N/m^2
            Rho = aRho;         // kg/m^3

            Alpha = 0.0;
        }


        /// <summary>
        /// Copy constructor.
        /// </summary>
        /// <param name="aMaterial">Material to copy</param>
        public Muscles_Material(Muscles_Material aMaterial)
        {
            Name = aMaterial.Name;
            Fy = aMaterial.Fy;           // N/m^2
            E = aMaterial.E;     // N/m^2
            Rho = aMaterial.Rho;         // kg/m^3

            Alpha = aMaterial.Alpha;
        }

        public Muscles_Material Duplicate()
        {
            return new Muscles_Material(this);
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
        ///
        /// >> "S235 Steel -- fy: 235Mpa - E: 210000MPa - ρ: 7850kg/m^3."
        /// </example>
        public override string ToString()
        {
            return $"{Name} -- E: {E * 1e-6:F2}MPa - fy: {Fy * 1e-6:F2}MPa - \u03c1: {Rho:F0}kg/m^3.";
        }

        #endregion Methods

    }
}