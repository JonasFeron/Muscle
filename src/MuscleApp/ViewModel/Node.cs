// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using MuscleCore.FEModel;

namespace MuscleApp.ViewModel
{
    public class Node
    {
        #region Properties
        public string TypeName { get { return "Node"; } }
        public int Idx { get; set; } //index of the node in the structure

        public Point3d Coordinates { get; set; }
        public bool IsValid { get { return true; } } //to implement


        ///// Support informations /////
        #region Support

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
        /// return the number (0,1,2, or 3) of fixed translations.
        /// </summary>
        public int FixationsCount
        {
            get { return Convert.ToInt16(!isXFree) + Convert.ToInt16(!isYFree) + Convert.ToInt16(!isZFree); }
        }

        public Vector3d Reactions { get; set; }

        #endregion Support

        ///// Load informations /////
        #region Load

        public Vector3d Loads { get; set; }
        //public Vector3d LoadToApply { get; set; }

        public Vector3d Residuals { get; set; } // the unbalanced loads = Load - SUM Tension*cos
                                               //public Vector3d PrestressLoad_To_Apply { get; set; } // load coming from an initial force


        #endregion Load

        ///// Displacement informations /////
        #region Displacement
        // Only keep the current nodal coordinates into Point. 
        #endregion Displacement

        #endregion Properties


        #region Constructors
        /// <summary>
        /// Initialize all properties to default value
        /// </summary>
        private void Init()
        {
            Idx = -1;
            Coordinates = new Point3d();

            isXFree = true;
            isYFree = true;
            isZFree = true;

            Reactions = new Vector3d();
            Loads = new Vector3d();
            Residuals = new Vector3d();
        }
        public Node()
        {
            Init();
        }
        public Node(Point3d point)
        {
            Init();
            Coordinates = point;
        }
        public Node(Point3d point, int idx)
        {
            Init();
            Coordinates = point;
            Idx = idx;
        }


        public Node(Node other)
        {
            Idx = other.Idx;
            Coordinates = other.Coordinates;

            isXFree = other.isXFree;
            isYFree = other.isYFree;
            isZFree = other.isZFree;

            Reactions = other.Reactions;
            Loads = other.Loads;
            Residuals = other.Residuals;
        }

        public Node Copy() //Duplication method calling the copy constructor
        {
            return new Node(this);
        }


        #endregion Constructors



        #region Methods

        public override string ToString()
        {
            return $"Node {Idx} with coordinates {Coordinates}";
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
        public void AddSupportIfSamePoint(Support support, double ZeroGeometricATol)
        {
            if (Coordinates.EpsilonEquals(support.Point, ZeroGeometricATol))
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
        /// <param name="ZeroGeometricATol"></param> the max distance (in m) between 2 points to be considered as equal. 
        /// <returns></returns>
        public static bool EpsilonContains(List<Point3d> points, Point3d thePoint, double ZeroGeometricATol, out int ind)
        {

            if (points == null || points.Count == 0)
            {
                ind = -1;
                return false;
            }
            ind = 0;
            foreach (Point3d point in points) // all point of the list is checked
            {
                if (point.EpsilonEquals(thePoint, ZeroGeometricATol)) { return true; } // as soon as a point from the list is equal to thePoint within the tolerance eps, then the list contains thePoint == true and exit. 
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
            List<Point3d> points = nodes.Select(n => n.Coordinates).ToList(); //transform the list of nodes into a list of Point
            return EpsilonContains(points, thePoint, ZeroTol, out ind);
        }
        #endregion List<Node>Methods

        #endregion Methods
    }
}
