     
using Muscle.Elements;
using Muscle.Nodes;
using Muscle.Structure;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

namespace Muscle.FEModel
{
	public class FEM_NodesResults
	{
        #region Nodes
		public double[][] NodesCoord { get; set; }  //[m] - shape (NodesCount,3)

		public double[][] Loads { get; set; } //[N] - shape (NodesCount,3)
		public double[][] Residual { get; set; } //[N] - shape (NodesCount,3)
		#endregion Nodes

  