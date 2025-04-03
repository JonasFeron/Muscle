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

using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using System.Collections.Generic;

namespace MuscleApp.ViewModel
{
    public class PointLoad
    {

        #region Properties

        //there are 3 ways to input a point Load. On a point, on a NodeIndex or on the Node. 
        public Point3d Point { set; get; }
        public int NodeIdx { set; get; }

        public Vector3d Vector { set; get; }

        public bool IsValid
        {
            get
            {
                // A point load is valid if it has a valid vector AND either:
                // 1. A valid point (for point-based loads) OR
                // 2. A valid node index (for node-based loads)
                return Vector.IsValid && (Point.IsValid || NodeIdx >= 0);
            }
        }


        #endregion Properties

        #region Constructors

        public PointLoad()
        {
            Point = new Point3d();
            Vector = new Vector3d();
        }

        public PointLoad(Point3d aPoint, Vector3d aVector)
        {
            Point = aPoint;
            Vector = aVector;
            NodeIdx = -1;
        }
        public PointLoad(Node aNode, Vector3d aVector)
        {
            NodeIdx = aNode.Idx;
            Point = aNode.Coordinates;
            Vector = aVector;
        }
        public PointLoad(int ind, Vector3d aVector)
        {
            NodeIdx = ind;
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
            if (load1.Point.EpsilonEquals(load2.Point, 1e-5)) { throw new System.Exception("Loads must have the same application point"); }

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
            if (NodeIdx == -1) return $"Point Load of {Vector3d.Multiply(1e-3, Vector).ToString()}kN applied on node [{Point.ToString()}].";
            else return $"Point Load of {Vector3d.Multiply(1e-3, Vector).ToString()}kN applied on node {NodeIdx}.";

        }



        #endregion Methods

    }
}
