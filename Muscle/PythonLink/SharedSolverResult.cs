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

namespace Muscle.PythonLink
{
	public class SharedSolverResult
	{
		#region Properties

		public string TypeName { get { return "SharedSolverResult"; } }
		public bool IsInEquilibrium { get; set; }

		#region Nodes
		public List<List<double>> NodesCoord { get; set; }  //[m] - shape (NodesCount,3)

		public List<List<double>> Loads { get; set; } //[N] - shape (NodesCount,3)
		public List<List<double>> Residual { get; set; } //[N] - shape (NodesCount,3)
		#endregion Nodes


		#region Elements
		public List<double> Tension { get; set; } //[N] - shape (ElementsCount,)
		public List<double> ElementsLFree { get; set; } //[m] - shape (ElementsCount,)

		#endregion Elements


		#region Supports
		public List<double> Reactions { get; set; } //[N] - shape (FixationsCount,)

		#endregion Supports

		#region StructureAnalysis
		// Performance of the DR method
		public int nTimeStep { get; set; }
		public int nKEReset { get; set; }

		#endregion StructureAnalysis

		#region Dynamics
		// Results of the dynamic component
		public int NumberOfFrequency { get; set; }
		public List<double> Frequency { get; set; } // Natural frequencies of the structure
		public List<List<double>> Modes { get; set; } //Mode of the structure ranked in the same way than the frequencies
		#endregion Dynamics

		///// Results informations /////



		#endregion Properties

		#region Constructors


		/// <summary>
		/// Initialize all Properties
		/// </summary>
		private void Init()
		{
			IsInEquilibrium = false;
			NodesCoord = new List<List<double>>();
			Loads = new List<List<double>>();
			Residual = new List<List<double>>();
			Tension = new List<double>();
			ElementsLFree = new List<double>();
			Reactions = new List<double>();
			nTimeStep = 0;
			nKEReset = 0;
			NumberOfFrequency = 0;
			Frequency = new List<double>();
			Modes = new List<List<double>>();
		}


		/// <summary>
		/// Default constructor
		/// </summary>
		public SharedSolverResult()
		{
			Init();
		}


		#endregion Constructors

		#region Methods
		public GH_Structure<GH_Number> ListListToGH_Struct(List<List<double>> datalistlist)
		{
			GH_Path path;
			int i = 0;
			GH_Structure<GH_Number> res = new GH_Structure<GH_Number>();
			foreach (List<double> datalist in datalistlist)
			{
				path = new GH_Path(i);
				res.AppendRange(datalist.Select(data => new GH_Number(data)), path);
				i++;
			}
			return res;
		}
		#endregion Methods

	}
}
