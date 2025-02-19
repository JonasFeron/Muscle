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
	public class FEM_ElementsResults
	{
		#region Properties

		public double[] Tension { get; set; } //[N] - shape (ElementsCount,)
		public double[] ElasticElongation { get; set; } //[m] - shape (ElementsCount,)

		#endregion Properties

		#region Constructors
		public FEM_ElementsResults()
		{
			Tension = new double[] { };
			ElasticElongation = new double[] { };
		}
		#endregion Constructors
	}
}
