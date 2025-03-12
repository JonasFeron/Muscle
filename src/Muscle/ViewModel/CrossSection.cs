using Rhino.Geometry;
using System;
using Grasshopper.Kernel.Types;

/* Modification non fusionnée à partir du projet 'Muscle (net48)'
Ajouté :
using Muscle;
using Muscle.CrossSections;
using Muscle.ViewModel;
*/

namespace Muscle.ViewModel
{
    /// <summary>
    /// Interface of CrossSection implement this to create new cross section
    /// </summary>
    public interface ICrossSection
    {

        #region Properties
        string ShapeName { get; }
        double Dimension { get; set; } //external diameter or side in [m]
        double Thickness { get; set; } //in [m]
        double DoverT { get; } // ratio Dimension/Thickness
        double Area { get; } //m2
        double Inertia { get; } //m4

        double q { get; }
        bool IsValid { get; }

        #endregion Properties

        #region Methods

        ICrossSection Copy();

        Curve InnerProfile(Point3d aPoint, Vector3d aNormal);

        Curve InnerProfile(Point3d aPoint, Plane aPlane);

        Curve OuterProfile(Point3d aPoint, Vector3d aNormal);

        Curve OuterProfile(Point3d aPoint, Plane aPlane);

        // Not supported yet so it's access modifer should be private.
        string ToString();

        #endregion Methods

    }

    public class CS_Circular : ICrossSection
    {

        #region Fields

        private const double pi = Math.PI;

        #endregion Fields

        #region Properties

        public string ShapeName
        {
            get
            {
                if (DoverT == 2.0) { return "Full Circular"; }
                else return "Hollow Circular ";
            }
        }

        public double Thickness { get; set; }

        public double Dimension { get; set; }

        public double DoverT
        {
            get { return Dimension / Thickness; }
        }

        public double Area
        {
            get { return pi / 4.0 * (Math.Pow(Dimension, 2.0) - Math.Pow(Dimension - 2.0 * Thickness, 2.0)); }
        }


        public double Inertia
        {
            get { return pi / 64.0 * (Math.Pow(Dimension, 4.0) - Math.Pow(Dimension - 2.0 * Thickness, 4.0)); }
        }

        public double q
        {
            get { return (double)(Inertia / Math.Pow(Area, 2.0)); }
        }

        public bool IsValid
        {
            get
            {
                if (Thickness > 0.0 && Thickness <= Dimension / 2.0 && Dimension > 0.0 && Area > 0.0 && Inertia > 0.0)
                {
                    return true;
                }
                else return false;
            }
        }


        #endregion Properties

        #region Constructors

        public CS_Circular()
        {
            Thickness = 0.0;
            Dimension = 0.0;
        }

        public CS_Circular(double aDiameter, double aThickness)
        {
            double t = aThickness;
            double d = aDiameter;
            if (aThickness >= aDiameter / 2.0) { t = aDiameter / 2.0; }
            if (aThickness <= 0.0) { t = aDiameter / 2.0; }
            if (aDiameter < 0.0) { d = 0.0; t = 0.0; }
            Thickness = t;
            Dimension = d;
        }

        public CS_Circular(ICrossSection aCrossSection)
        {
            Thickness = aCrossSection.Thickness;
            Dimension = aCrossSection.Dimension;
        }

        #endregion Constructors

        #region Methods

        public ICrossSection Copy()
        {
            return new CS_Circular(this);
        }

        public Curve InnerProfile(Point3d aPoint, Vector3d aNormal)
        {
            return new Circle(new Plane(aPoint, aNormal), Dimension / 2.0 - Thickness).ToNurbsCurve();
        }

        public Curve InnerProfile(Point3d aPoint, Plane aPlane)
        {
            return new Circle(aPlane, Dimension / 2.0 - Thickness).ToNurbsCurve();
        }

        public Curve OuterProfile(Point3d aPoint, Vector3d aNormal)
        {
            return new Circle(new Plane(aPoint, aNormal), Dimension / 2.0).ToNurbsCurve();
        }

        public Curve OuterProfile(Point3d aPoint, Plane aPlane)
        {
            return new Circle(aPlane, Dimension / 2.0).ToNurbsCurve();
        }

        public override string ToString()
        {
            return $"Cross Section: {ShapeName} -- \u03a6:{Dimension * 1e3:F0}mm - t:{Thickness * 1e3:F1}mm - A:{Area * 1e6:F0}mm^2 - I:{Inertia * 1e12:e4}mm^4";
        }

        #endregion Methods

    }

    public class CS_Square : ICrossSection
    {

        #region Properties
        public string ShapeName
        {
            get
            {
                if (DoverT == 2.0) { return "Full Square"; }
                else return "Hollow Square ";
            }
        }
        public double Dimension { get; set; }
        public double Thickness { get; set; }


        public double DoverT
        {
            get { return Dimension / Thickness; }
        }

        public double Area { get { return Math.Pow(Dimension, 2.0) - Math.Pow(Dimension - 2.0 * Thickness, 2.0); } }

        public double Inertia { get { return (Math.Pow(Dimension, 4.0) - Math.Pow(Dimension - 2.0 * Thickness, 4.0)) / 12.0; } }

        public double q
        {
            get { return (double)(Inertia / Math.Pow(Area, 2.0)); }
        }

        public bool IsValid
        {
            get
            {
                if (Thickness > 0.0 && Thickness <= Dimension / 2.0 && Dimension > 0.0 && Area > 0.0 && Inertia > 0.0)
                {
                    return true;
                }
                return false;
            }
        }

        #endregion Properties

        #region Constructors

        public CS_Square()
        {
            Thickness = 0.0f;
            Dimension = 0.0f;
        }

        public CS_Square(double aDiameter, double aThickness)
        {
            double t = aThickness;
            double d = aDiameter;
            if (aThickness >= aDiameter / 2.0) { t = aDiameter / 2.0f; }
            if (aThickness <= 0.0) { t = aDiameter / 2.0f; } // a null or negative thickness is transformed into a full square section.
            if (aDiameter < 0.0) { d = 0.0f; t = 0.0f; }
            Thickness = t;
            Dimension = d;
        }

        public CS_Square(ICrossSection aCrossSection)
        {
            Thickness = aCrossSection.Thickness;
            Dimension = aCrossSection.Dimension;
        }

        #endregion Constructors

        #region Methods

        public ICrossSection Copy()
        {
            return new CS_Square(this);
        }

        public Curve InnerProfile(Point3d aPoint, Vector3d aNormal)
        {
            Plane nPlane = new Plane(aPoint, aNormal);
            nPlane.Translate(-nPlane.XAxis * Dimension / 2.0 - nPlane.YAxis * Dimension / 2.0);
            return new Rectangle3d(nPlane, Dimension - 2.0 * Thickness, Dimension - 2.0 * Thickness).ToNurbsCurve();
        }

        public Curve InnerProfile(Point3d aPoint, Plane aPlane)
        {
            Plane nPlane = aPlane;
            nPlane.Translate(-nPlane.XAxis * Dimension / 2.0 - nPlane.YAxis * Dimension / 2.0);

            return new Rectangle3d(nPlane, Dimension - 2.0 * Thickness, Dimension - 2.0 * Thickness).ToNurbsCurve();

        }

        public Curve OuterProfile(Point3d aPoint, Vector3d aNormal)
        {
            Plane nPlane = new Plane(aPoint, aNormal);
            nPlane.Translate(-nPlane.XAxis * Dimension / 2.0 - nPlane.YAxis * Dimension / 2.0);
            return new Rectangle3d(nPlane, Dimension, Dimension).ToNurbsCurve();
        }

        public Curve OuterProfile(Point3d aPoint, Plane aPlane)
        {
            Plane nPlane = aPlane;
            nPlane.Translate(-nPlane.XAxis * Dimension / 2.0 - nPlane.YAxis * Dimension / 2.0);
            return new Rectangle3d(nPlane, Dimension, Dimension).ToNurbsCurve();
        }

        public override string ToString()
        {
            return $"Cross Section: {ShapeName} -- W:{Dimension * 1e3:F1}mm - t:{Thickness * 1e3:F1}mm - A:{Area * 1e6:F0}mm^2 - I:{Inertia * 1e12:e4}mm^4";
        }

        #endregion Methods

    }
}