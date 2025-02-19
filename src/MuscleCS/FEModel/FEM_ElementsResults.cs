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

		// public string TypeName { get { return "SharedSolverResult"; } }
		// public bool IsInEquilibrium { get; set; }

		// #region Nodes
		// public List<List<double>> NodesCoord { get; set; }  //[m] - shape (NodesCount,3)

		// public List<List<double>> Loads { get; set; } //[N] - shape (NodesCount,3)
		// public List<List<double>> Residual { get; set; } //[N] - shape (NodesCount,3)
		// #endregion Nodes


		#region Elements
		public double[] Tension { get; set; } //[N] - shape (ElementsCount,)
		public double[] ElementsLFree { get; set; } //[m] - shape (ElementsCount,)

		#endregion Elements


		// #region Supports
		// public List<double> Reactions { get; set; } //[N] - shape (FixationsCount,)

		// #endregion Supports

		// #region StructureAnalysis
		// // Performance of the DR method
		// public int nTimeStep { get; set; }
		// public int nKEReset { get; set; }

		// #endregion StructureAnalysis

		// #region Dynamics
		// // Results of the dynamic component
		// public int NumberOfFrequency { get; set; } //Number of frequency computed
		// public List<double> Frequency { get; set; } // Natural frequencies of the structure
		// public List<List<double>> Modes { get; set; } //Mode of the structure ranked in the same way than the frequencies

		// public List<double> DynMasses { get; set; } //Masses used for the dynamic computation
		// #endregion Dynamics

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
			DynMasses = new List<double>();

		}


		/// <summary>
		/// Default constructor
		/// </summary>
		public SharedSolverResult()
		{
			Init();
		}


		#endregion Constructors



	}
}
