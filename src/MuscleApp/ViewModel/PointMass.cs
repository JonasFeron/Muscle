using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;
using Rhino.Geometry;
using System.Collections.Generic;

namespace MuscleApp.ViewModel
{
    public class PointMass
    {

        #region Properties

        public Point3d Point { set; get; } = new Point3d();
        public int NodeInd { set; get; } = -1;

        public Vector3d Vector { set; get; } = new Vector3d(); 

        #endregion Properties

        #region Constructors

        //Different way to initialize a point mass
        public PointMass() //Contain a mass in kg 
        {
        }

        public PointMass(Point3d aPoint, Vector3d aVector)
        {
            Point = aPoint;
            Vector = aVector;
            NodeInd = -1;
        }
        public PointMass(Node aNode, Vector3d aVector)
        {
            NodeInd = aNode.Idx;
            Point = aNode.Coordinates;
            Vector = aVector;
        }
        public PointMass(int ind, Vector3d aVector)
        {
            NodeInd = ind;
            Vector = aVector;
        }
        public PointMass(Point3d aPoint, double mass)
        {
            Point = aPoint;
            Vector = new Vector3d(mass, mass, mass);
            NodeInd = -1;
        }
        public PointMass(Node aNode, double mass)
        {
            NodeInd = aNode.Idx;
            Point = aNode.Coordinates;
            Vector = new Vector3d(mass, mass, mass);
        }
        public PointMass(int ind, double mass)
        {
            NodeInd = ind;
            Vector = new Vector3d(mass, mass, mass);
        }

        public PointMass(PointMass aPointMass)
        {
            Point = aPointMass.Point;
            Vector = aPointMass.Vector;
        }

        #endregion Constructors



        #region Methods
        public static PointMass operator *(PointMass mass, double factor)
        {
            return new PointMass()
            {
                Point = mass.Point,
                Vector = mass.Vector * factor
            };
        }

        public static PointMass operator +(PointMass mass1, PointMass mass2)
        {
            if (mass1.Point.EpsilonEquals(mass2.Point, 1e-5)) { throw new System.Exception("Mass must have the same application point"); }

            return new PointMass()
            {
                Point = mass1.Point,
                Vector = mass1.Vector + mass2.Vector,
            };
        }

        public PointMass Duplicate()
        {
            return new PointMass(this);
        }

        public override string ToString() //Text description
        {
            if (NodeInd == -1) return $"Point mass of {Vector.Z.ToString()}kg applied on node [{Point.ToString()}].";
            else return $"Point mass of {Vector.Z.ToString()}kg applied on node {NodeInd}.";

        }
        #endregion Methods
    }
}
