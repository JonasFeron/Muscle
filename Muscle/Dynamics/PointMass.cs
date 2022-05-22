using Grasshopper.Kernel.Types;
using Muscle.Nodes;
using Muscle.Structure;
using Rhino.Geometry;
using System.Collections.Generic;

namespace Muscle.Dynamics
{
    public class PointLoad
    {

        #region Properties

        //there are 3 ways to input a point Load. On a point, on a NodeIndex or on the Node. 
        public Point3d Point { set; get; }
        public int NodeInd { set; get; }

        public Vector3d Vector { set; get; }

        #endregion Properties

        #region Constructors

        public PointLoad() //Contain a mass in kg 
        {
            Point = new Point3d();
            Vector = new Vector3d();
        }

        public PointLoad(Point3d aPoint, Vector3d aVector)
        {
            Point = aPoint;
            Vector = aVector;
            NodeInd = -1;
        }
        public PointLoad(Node aNode, Vector3d aVector)
        {
            NodeInd = aNode.Ind;
            Vector = aVector;
        }
        public PointLoad(int ind, Vector3d aVector)
        {
            NodeInd = ind;
            Vector = aVector;
        }


        public PointLoad(PointLoad aPointLoad)
        {
            Point = aPointLoad.Point;
            Vector = aPointLoad.Vector;
        }

        #endregion Constructors

        #region Methods

        public static PointLoad operator *(PointLoad load, double factor)
        {
            return new PointLoad()
            {
                Point = load.Point,
                Vector = load.Vector * factor
            };
        }

        public static PointLoad operator +(PointLoad load1, PointLoad load2)
        {
            if (load1.Point.EpsilonEquals(load2.Point, 1e-5)) { throw new System.Exception("Mass must have the same application point"); }

            return new PointLoad()
            {
                Point = load1.Point,
                Vector = load1.Vector + load2.Vector,
            };
        }

        public PointLoad Duplicate()
        {
            return new PointLoad(this);
        }

        public override string ToString()
        {
            if (NodeInd == -1) return $"Point Load of {Vector3d.Multiply(1e-3, Vector).ToString()}kN applied on node [{Point.ToString()}].";
            else return $"Point Load of {Vector3d.Multiply(1e-3, Vector).ToString()}kN applied on node {NodeInd}.";

        }



        #endregion Methods

    }
}
