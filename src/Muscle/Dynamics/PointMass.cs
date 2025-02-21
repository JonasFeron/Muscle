using Grasshopper.Kernel.Types;
using Muscle.Structure;
using Muscle.ViewModel;
using Rhino.Geometry;
using System.Collections.Generic;

namespace Muscle.Dynamics
{
    public class PointMass
    {

        #region Properties

        //there is 1 ways to input a point mass:  on a NodeIndex 
        //During the dynamic computation, this point mass is linked to a node with his coordinates 'Poind3d Point'

        public Point3d Point { set; get; }
        public int NodeInd { set; get; }

        public Vector3d Vector { set; get; } //Will contain in the z direction the mass in [kg]

        #endregion Properties

        #region Constructors

        //Different way to initialize a point mass
        public PointMass() //Contain a mass in kg 
        {
            Point = new Point3d();
            Vector = new Vector3d();
        }

        public PointMass(Point3d aPoint, Vector3d aVector)
        {
            Point = aPoint;
            Vector = aVector;
            NodeInd = -1;
        }
        public PointMass(Node aNode, Vector3d aVector)
        {
            NodeInd = aNode.Ind;
            Vector = aVector;
        }
        public PointMass(int ind, Vector3d aVector)
        {
            NodeInd = ind;
            Vector = aVector;
        }

        public PointMass(int ind, Point3d point, Vector3d aVector)
        {
            NodeInd = ind;
            Point = point;
            Vector = aVector;
        }

        public PointMass(PointMass aPointMass)
        {
            Point = aPointMass.Point;
            Vector = aPointMass.Vector;
        }

        #endregion Constructors



        #region Methods
        public static PointMass operator *(PointMass load, double factor)
        {
            return new PointMass()
            {
                Point = load.Point,
                Vector = load.Vector * factor
            };
        }

        public static PointMass operator +(PointMass load1, PointMass load2)
        {
            if (load1.Point.EpsilonEquals(load2.Point, 1e-5)) { throw new System.Exception("Mass must have the same application point"); }

            return new PointMass()
            {
                Point = load1.Point,
                Vector = load1.Vector + load2.Vector,
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
