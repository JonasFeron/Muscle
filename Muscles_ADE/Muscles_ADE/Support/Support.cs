using Muscles_ADE.Nodes;
using Muscles_ADE.Structure;
using Rhino.Geometry;

using System;
using System.Collections.Generic;

namespace Muscles_ADE
{

    public class Support
    {

        #region Properties

        ///// <summary>
        ///// True if at least one translation is fixed
        ///// </summary>
        //public bool IsUseful { get { return (isXFree || isYFree || isZFree); } }

        /// <summary>
        /// True if point is Free to move in X dir. False if fixed.
        /// </summary>
        public bool isXFree { get; set; }

        /// <summary>
        /// True if point is Free to move in Y dir. False if fixed.
        /// </summary>
        public bool isYFree { get; set; }

        /// <summary>
        /// True if point is Free to move in Z dir. False if fixed.
        /// </summary>
        public bool isZFree { get; set; }

        /// <summary>
        /// return the number (0,1,2, or 3) of fixed translations. False if fixed.
        /// </summary>
        public int FixationCount
        {
            get { return Convert.ToInt16(!isXFree) + Convert.ToInt16(!isYFree) + Convert.ToInt16(!isZFree); }
        }

        /// <summary>
        /// Point of application of the support
        /// </summary>
        public Point3d Point { get; set; }

        #endregion Properties

        #region Constructors

        /// <summary>
        /// The default constructor creates a support on the default point and fixes its X, Y and Z translations.
        /// </summary>
        public Support()
        {
            Point = new Point3d();

            isXFree = false;
            isYFree = false;
            isZFree = false;
        }

        /// <summary>
        /// The constructor creates a support on a given point and fixes its X, Y and Z translations.
        /// </summary>
        /// <param name="point">Point of application of the support.</param>
        public Support(Point3d point)
        {
            Point = point;

            isXFree = false;
            isYFree = false;
            isZFree = false;
        }

        /// <summary>
        /// The constructor creates a support on a given point and fixes its given translations.
        /// </summary>
        /// <param name="point">Point of application of the support.</param>
        /// <param name="Xfree">Is the X translation free ?</param>
        /// <param name="Yfree">Is the Y translation free ?</param>
        /// <param name="Zfree">Is the Z translation free ?</param>
        public Support(Point3d point, bool Xfree, bool Yfree, bool Zfree)
        {
            Point = point;
            isXFree = Xfree;
            isYFree = Yfree;
            isZFree = Zfree;
        }

        /// <summary>
        /// Copy constructor.
        /// </summary>
        /// <param name="support">Support to copy.</param>
        public Support(Support support)
        {
            Point = support.Point;
            isXFree = support.isXFree;
            isYFree = support.isYFree;
            isZFree = support.isZFree;
        }

        /// <summary>
        /// return a new support with merged fixation conditions in X Y and/or Z according to support1 and 2. If Support 1 and 2 are not defined on the same point, the merged support is defined on point1.
        /// </summary>
        /// <example>
        /// >> Support s1 = new Support(new Point(1.0, 2.0, 3.0), true, false, false)) // X is fixed
        /// >> Support s2 = new Support(new Point(1.0, 2.0, 3.0), false, false, true)) // Z is fixed
        /// >> Support s3 = MergeConditionsOf(s1,s2); // s3 is fixed in X and Z
        /// </example>
        /// 
        public static Support MergeConditionsOf(Support support1, Support support2)
        {
            Support merged_support = support1.Duplicate(); //
            merged_support.isXFree = support1.isXFree && support2.isXFree; // True (=Free) if both conditions are True
            merged_support.isYFree = support1.isYFree && support2.isYFree; // False(=Fixed) if at least 1 condition is False
            merged_support.isZFree = support1.isZFree && support2.isZFree;
            return merged_support;
        }
        #endregion Constructors

        #region Methods

        public Support Duplicate()
        {
            return new Support(this);
        }

        /// <summary>
        /// Return human readable text describing the support.
        /// </summary>
        public override string ToString()
        {

            if (FixationCount == 0)
            {
                return $"Point [{Point.ToString()}] is free to move !";
            }

            string message = $"Point [{Point.ToString()}] is fixed in the ";
            if (!isXFree) { message += "X "; }

            if (!isYFree) { message += "Y "; }

            if (!isZFree) { message += "Z "; }

            if (FixationCount == 1) { return message + "direction."; }
            else { return message + "directions."; }
        }

        /// <summary>
        /// Return a list of supports which have only one support per point. The fixing conditions are merged if there are differents supports defined on the same point in the inputted list.
        /// </summary>
        /// <param name="supports"></param> a list of support which may have more than one support defined on the same points
        /// <returns></returns>
        public static List<Support> MergeConditionsOnSamePoint(List<Support> supports)
        {
            List<Support> merged_supports = new List<Support>();
            List<Point3d> points = new List<Point3d>();

            Support duplicated_support;
            Support merged_support;
            Point3d current_point;
            int ind;

            foreach (Support current_support in supports)
            {
                current_point = current_support.Point;
                if (Node.EpsilonContains(points, current_point, 1e-5f, out ind)) //si un support est déjà défini sur le point (X,Y,Z) courant (au centième de mm près).
                {
                    //alors on rassemble les conditions d'appuis dans un nouveau support et on retire le premier support de la liste. 
                    duplicated_support = merged_supports[ind]; // on récupère le premier support dans la liste
                    merged_support = MergeConditionsOf(duplicated_support, current_support); //on crée un nouveau support rassemblant les conditions des 2 supports
                    points.RemoveAt(ind);
                    merged_supports.RemoveAt(ind);
                    points.Add(current_point);
                    merged_supports.Add(merged_support);
                }
                else
                {
                    points.Add(current_point);
                    merged_supports.Add(current_support);
                }
            }
            return merged_supports;
        }

        #endregion Methods

    }
}