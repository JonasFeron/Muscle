using Muscle.Elements;
using Muscle.Nodes;
//using Muscle.Solvers;
using Muscle.Structure;
//using Muscle.Dynamics;
using Rhino.Geometry;
using System;
using System.Collections.Generic;


namespace Muscle.FEModel
{
	public class FEM_Elements
	{
		#region Properties





		#region Elements
		public int[] ElementsType { get; set; } //shape (ElementsCount, )
		public int[,] ElementsEndNodes { get; set; } //shape (ElementsCount, 2)
		public double[,] ElementsA { get; set; } // [mm²] - shape (ElementsCount, 2) - Area in Compression and Area in Tension of the Elements
		public double[,] ElementsE { get; set; } // [MPa] - shape (ElementsCount, 2) - Young Modulus in Compression and in Tension of the Elements
		public double[] TensionInit { get; set; }
		public double[] ElementsLFreeInit { get; set; }
		public double[] LengtheningsToApply { get; set; }

		#endregion Elements




		// #region SolverInputs
		// public double Residual0Threshold { get; set; }
		// public double Dt { get; set; }
		// public double AmplMass { get; set; }
		// public double MinMass { get; set; }
		// public int MaxTimeStep { get; set; }
		// public int MaxKEReset { get; set; }
		// public int n_steps { get; set; } // number of steps for the non-linear solver


		// #endregion SolverInputs

		// #region Dynamics
		// //Variables for the dynamic computation
		// public List<double> DynamicMass { get; set; } //Mass applied at each node for the dynamics computation

		// public List<double> MassElement { get; set; } //Mass list containting all the masses of the element. Enable the construction of the CONSISTENT MASS matrix.

		// public int MaxFreqWanted { get; set; } //Maximum frequencies and modes that the user want to obtain

		// #endregion Dynamics 


		#endregion Properties

		#region Constructors


		/// <summary>
		/// Initialize all Properties
		/// </summary>
		private void Init()
		{
			n_steps = 1;
			ElementsType = new List<int>();
			NodesCoord = new List<List<double>>();
			LoadsInit = new List<List<double>>();
			LoadsToApply = new List<List<double>>();
			ElementsEndNodes = new List<List<int>>();
			ElementsA = new List<List<double>>();
			ElementsE = new List<List<double>>();
			TensionInit = new List<double>();
			ElementsLFreeInit = new List<double>();
			LengtheningsToApply = new List<double>();
			IsDOFfree = new List<bool>();
			ReactionsInit = new List<double>();
			Residual0Threshold = 0.0001;
			DynamicMass = new List<double>();
			MassElement = new List<double>();
			MaxFreqWanted = 0;
		}


		/// <summary>
		/// Default constructor
		/// </summary>
		public SharedData()
		{
			Init();
		}

		public SharedData(StructureObj structObj)
		{
			Init();
			RegisterElements(structObj);
			RegisterNodes(structObj);
			//RegisterDRMethodParameters(structObj.DR);
		}

		// public SharedData(StructureObj structObj, int number_steps)
		// {
		// 	Init();
		// 	RegisterElements(structObj);
		// 	RegisterNodes(structObj);
		// 	n_steps = number_steps;
		// }

		// public SharedData(StructureObj structObj, List<double> DynMass, int MaxFreqWtd) //For the dynamic computation
		// {
		// 	Init();
		// 	RegisterElements(structObj);
		// 	RegisterNodes(structObj);
		// 	DynamicMass = DynMass;
		// 	MaxFreqWanted = MaxFreqWtd;
		// }

		// public SharedData(StructureObj structObj, List<double> DynMass, List<double> MassAllElements, int MaxFreqWtd) //For the dynamic CONSISTENT computation
		// {
		// 	Init();
		// 	RegisterElements(structObj);
		// 	RegisterNodes(structObj);
		// 	DynamicMass = DynMass;
		// 	MassElement = MassAllElements;
		// 	MaxFreqWanted = MaxFreqWtd;
		// }

		#endregion Constructors


		// #region Methods
		// /// <summary>
		// /// No Need to recompute the Assembly of the structure if the geometry has not changed. A geometry only consist in Nodes coordinates, ElementsEndNodes, IsDOFfree.
		// /// </summary>
		// /// <param name="obj"></param>
		// /// <returns></returns>
		// public bool HasSameGeometryThan(object obj)
		// {
		// 	//Check for null and compare run-time types.
		// 	if ((obj == null) || !this.GetType().Equals(obj.GetType()))
		// 	{
		// 		return false;
		// 	}
		// 	SharedData other = (SharedData)obj;

		// 	if (this.NodesCoord.Count != other.NodesCoord.Count) return false;
		// 	for (int i = 0; i < NodesCoord.Count; i++)
		// 	{
		// 		for (int j = 0; j < 3; j++)
		// 		{
		// 			double double1 = this.NodesCoord[i][j];
		// 			double double2 = other.NodesCoord[i][j];
		// 			double difference = Math.Abs(double1 / 1e5);// Define the tolerance for variation in their values
		// 			if (Math.Abs(double1 - double2) > difference) return false;
		// 		}
		// 	}

		// 	if (this.ElementsEndNodes.Count != other.ElementsEndNodes.Count) return false;
		// 	for (int i = 0; i < ElementsEndNodes.Count; i++)
		// 	{
		// 		for (int j = 0; j < 2; j++)
		// 		{
		// 			if (ElementsEndNodes[i][j] != other.ElementsEndNodes[i][j]) return false;
		// 		}
		// 	}
		// 	if (this.IsDOFfree.Count != other.IsDOFfree.Count) return false;
		// 	for (int i = 0; i < IsDOFfree.Count; i++)
		// 	{
		// 		if (IsDOFfree[i] != other.IsDOFfree[i]) return false;
		// 	}

		// 	return true;
		// }

		private void RegisterElements(StructureObj structObj)
		{
			foreach (Element e in structObj.StructuralElements)
			{
				double[] A = new double[] { e.CS_Comp.Area * 1e6, e.CS_Tens.Area * 1e6 }; //Python in [mm^2], C# in [m^2]
				double[] E = new double[] { e.Mat_Comp.E / 1e6, e.Mat_Tens.E / 1e6 }; //Python in [MPa], C# in [Pa]
				double Tension = e.Tension;
				double LFree = e.LFree;
				double LengtheningToApply = structObj.LengtheningsToApply[e.Ind];

				ElementsType.Add(e.Type);
				ElementsEndNodes.Add(e.EndNodes);
				ElementsA.Add(A);
				ElementsE.Add(E);
				TensionInit.Add(Tension);
				ElementsLFreeInit.Add(LFree);
				LengtheningsToApply.Add(LengtheningToApply);
			}
		}



		#endregion Methods

	}
}