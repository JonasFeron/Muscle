using Muscles_ADE.Loads;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles_ADE.Nodes
{
    public class Node
    {
        #region Properties
        public string TypeName { get { return "Node"; } }
        public int Ind { get; set; } //index of the node in the structure

        public Point3d Point { get; set; }
        public bool IsValid { get { return true; } } //to implement


        ///// Support informations /////
        #region Support

        /// <summary>
        /// True if point is Free to move in X dir. False if fixed.
        /// </summary>
        public bool isXFree { get; set; }
        public int Ind_RX { get; set; } //-1 if free to move in X; Ind of the Reaction if fixed

        /// <summary>
        /// True if point is Free to move in Y dir. False if fixed.
        /// </summary>
        public bool isYFree { get; set; }
        public int Ind_RY { get; set; }


        /// <summary>
        /// True if point is Free to move in Z dir. False if fixed.
        /// </summary>
        public bool isZFree { get; set; }
        public int Ind_RZ { get; set; }

        /// <summary>
        /// return the number (0,1,2, or 3) of fixed translations.
        /// </summary>
        public int FixationsCount
        {
            get { return Convert.ToInt16(!isXFree) + Convert.ToInt16(!isYFree) + Convert.ToInt16(!isZFree); }
        }

        public Vector3d Reaction { get; set; }
        //public List<Vector3d> Reaction_Results { get; set; }
        //public List<Vector3d> Reaction_Total { get; set; } // addition of already applied + results

        #endregion Support

        ///// Load informations /////
        #region Load

        public Vector3d Load { get; set; }
        //public Vector3d LoadToApply { get; set; }

        public Vector3d Residual { get; set; } // the unbalanced loads = Load - SUM Tension*cos
        //public Vector3d PrestressLoad_To_Apply { get; set; } // load coming from an initial force

        //public List<Vector3d> Load_Results { get; set; }
        //public List<Vector3d> Load_Total { get; set; }


        #endregion Load

        ///// Displacement informations /////
        #region Displacement

        //public Vector3d Displacement_Already_Applied { get; set; }
        //public List<Vector3d> Displacement_Results { get; set; }
        //public List<Vector3d> Displacement_Total { get; set; } // addition of already applied + results

        #endregion Displacement

        #endregion Properties


        #region Constructors
        /// <summary>
        /// Initialize all properties to default value
        /// </summary>
        private void Init()
        {
            Ind = -1;
            Point = new Point3d();

            isXFree = true;
            isYFree = true;
            isZFree = true;
            Ind_RX = -1;
            Ind_RY = -1;
            Ind_RZ = -1;
            Reaction = new Vector3d();
            //Reaction_Results = new List<Vector3d>();
            //Reaction_Total = new List<Vector3d>();

            Load = new Vector3d();
            Residual = new Vector3d();
            //LoadToApply = new Vector3d();
            //Load_Results = new List<Vector3d>();
            //Load_Total = new List<Vector3d>();

            //Displacement_Already_Applied = new Vector3d();
            //Displacement_Results = new List<Vector3d>();
            //Displacement_Total = new List<Vector3d>();
        }
        public Node()
        {
            Init();
        }
        public Node(Point3d point)
        {
            Init();
            Point = point;
        }
        public Node(Point3d point, int ind)
        {
            Init();
            Point = point;
            Ind = ind;
        }
        public Node(Node other)
        {
            Ind = other.Ind;
            Point = other.Point;

            isXFree = other.isXFree;
            isYFree = other.isYFree;
            isZFree = other.isZFree;
            Ind_RX = other.Ind_RX;
            Ind_RY = other.Ind_RY;
            Ind_RZ = other.Ind_RZ;

            Reaction = other.Reaction;
            //Reaction_Results = other.Reaction_Results;
            //Reaction_Total = other.Reaction_Total;

            Load = other.Load;
            Residual = other.Residual;
            //LoadToApply = other.LoadToApply;
            //Load_Results = other.Load_Results;
            //Load_Total = other.Load_Total;

            //Displacement_Already_Applied = other.Displacement_Already_Applied;
            //Displacement_Results = other.Displacement_Results;
            //Displacement_Total = other.Displacement_Total;
        }
        public Node Duplicate() //Duplication method calling the copy constructor
        {
            return new Node(this);
        }
        #endregion Constructors



        #region Methods

        public override string ToString()
        {
            return $"Node {Ind} with coordinates {Point}";
        }

        ///// Methods related to this object /////
        #region NodeMethods

        /// <summary>
        /// Add the support conditions to the node (even if the support apply on another point). If two supports are added to a same node (for instance, one is Fixed in X and the other one is Free) then the more restraining condition (Fixed) is conserved.  
        /// </summary>
        /// <param name="support"></param>
        public void AddSupport(Support support)
        {
            isXFree = isXFree && support.isXFree; // True (=Free) if both conditions are True
            isYFree = isYFree && support.isYFree; // False(=Fixed) if at least 1 condition is False
            isZFree = isZFree && support.isZFree;
        }

        /// <summary>
        /// Add the support conditions to the node (if the support is applied on a point closer than ZeroTol otherwise do nothing). If two supports are added to a same node (for instance, one is Fixed in X and the other one is Free) then the more restraining condition (Fixed) is conserved.  
        /// </summary>
        public void AddSupportIfSamePoint(Support support, double ZeroTol)
        {
            if (Point.EpsilonEquals(support.Point, ZeroTol))
            {
                isXFree = isXFree && support.isXFree; // True (=Free) if both conditions are True
                isYFree = isYFree && support.isYFree; // False(=Fixed) if at least 1 condition is False
                isZFree = isZFree && support.isZFree;
            }
        }


        /// <summary>
        /// Add the Load to the node (if it is applied on a point closer than ZeroTol of the node otherwise do nothing).
        /// </summary>
        //public void AddLoadToApplyIfSamePoint(PointLoad load, double ZeroTol)
        //{
        //    if (Point.EpsilonEquals(load.Point, ZeroTol))
        //    {
        //        LoadToApply += load.Vector; 
        //    }
        //}

        ///// <summary>
        ///// Add the PressLoad to the node (if it is applied on a point closer than ZeroTol of the node otherwise do nothing).
        ///// </summary>
        //public void AddPrestressLoadToApplyIfSamePoint(PointLoad load, double ZeroTol)
        //{
        //    if (Point.EpsilonEquals(load.Point, ZeroTol))
        //    {
        //        PrestressLoad_To_Apply += load.Vector;
        //    }
        //}

        #endregion NodeMethods

        ///// Static Methods related to List<Point3d> /////
        #region List<Point3d>Methods

        /// <summary>
        /// Remove Duplicated points from the list and return therefore a smaller list. 
        /// </summary>
        /// <param name="points"></param> a list of points which may have duplicated points
        /// <returns></returns>
        public static List<Point3d> RemoveDuplicatedPoints(List<Point3d> points, double ZeroTol)
        {
            List<Point3d> pointsWithoutDuplicate = new List<Point3d>();
            int ind;
            foreach (Point3d point in points)
            {
                if (!EpsilonContains(pointsWithoutDuplicate, point, ZeroTol, out ind)) { pointsWithoutDuplicate.Add(point); } //if the point is not contained in the list of points without duplicate then we add it. 
            }
            return pointsWithoutDuplicate;
        }

        /// <summary>
        /// return True if the list of points contains thePoint within the ZeroTolerance ZeroTol. The index of thePoint in the list of Points is returned in ind parameter.
        /// </summary>
        /// <param name="points"></param> the list of points
        /// <param name="thePoint"></param> is thePoint contained in the list ?
        /// <param name="ZeroTol"></param> the max distance (in m) between 2 points to be considered as equal. 
        /// <returns></returns>
        public static bool EpsilonContains(List<Point3d> points, Point3d thePoint, double ZeroTol, out int ind)
        {

            if (points == null || points.Count == 0)
            {
                ind = -1;
                return false;
            }
            ind = 0;
            foreach (Point3d point in points) // all point of the list is checked
            {
                if (point.EpsilonEquals(thePoint, ZeroTol)) { return true; } // as soon as a point from the list is equal to thePoint within the tolerance eps, then the list contains thePoint == true and exit. 
                ind++;
            }
            ind = -1; // if the point do not belong to the list
            return false;
        }

        #endregion List<Point3d>Methods


        ///// Static Methods related to List<Node> /////
        #region List<Node>Methods
        public static bool EpsilonContains(List<Node> nodes, Point3d thePoint, double ZeroTol, out int ind)
        {
            List<Point3d> points = nodes.Select(n => n.Point).ToList(); //transform the list of nodes into a list of Point
            return EpsilonContains(points, thePoint, ZeroTol, out ind);
        }
        #endregion List<Node>Methods

        #endregion Methods
    }
}

