using Muscles_ADE.Elements;
using Muscles_ADE.Nodes;
using Muscles_ADE.Solvers;
using Muscles_ADE.Structure;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles_ADE.PythonLink
{
	public class SharedData
	{
		#region Properties

		public string TypeName { get { return "SharedData"; } }

		#region Nodes
		public List<List<double>> NodesCoord { get; set; } //shape (NodesCount, 3)
		public List<List<double>> LoadsInit { get; set; } //shape (NodesCount, 3)
		public List<List<double>> LoadsToApply { get; set; } //shape (NodesCount, 3)

		#endregion Nodes


		#region Elements
		public List<int> ElementsType { get; set; } //shape (ElementsCount, )

		public List<List<int>> ElementsEndNodes { get; set; } //shape (ElementsCount, 2)
		public List<List<double>> ElementsA { get; set; } // [mm²] - shape (ElementsCount, 2) - Area in Compression and Area in Tension of the Elements
		public List<List<double>> ElementsE { get; set; } // [MPa] - shape (ElementsCount, 2) - Young Modulus in Compression and in Tension of the Elements

		public List<double> TensionInit { get; set; }

		public List<double> ElementsLFreeInit { get; set; }

		public List<double> LengtheningsToApply { get; set; }

		#endregion Elements


		#region Supports
		public List<bool> IsDOFfree { get; set; } // [bool] - shape (3NodesCount,). Each point i is associated to its X DOF (3i), Y DOF (3i+1), Z DOF (3i+2). Each DOF can be fixed (False) or free (True).

		public List<double> ReactionsInit { get; set; }
		#endregion Supports

		#region SolverInputs
		public double Residual0Threshold { get; set; }
		public double Dt { get; set; }
		public double AmplMass { get; set; }
		public double MinMass { get; set; }
		public int MaxTimeStep { get; set; }
		public int MaxKEReset { get; set; }
		public int n_steps { get; set; } // number of steps for the non-linear solver

		public int DynMasses { get; set; } //Added for dyn

		#endregion SolverInputs

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
			DynMasses = new int();
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
			RegisterDRMethodParameters(structObj.DR);
		}

		public SharedData(StructureObj structObj, int number_steps)
		{
			Init();
			RegisterElements(structObj);
			RegisterNodes(structObj);
			n_steps = number_steps;
		}



		#endregion Constructors


		#region Methods
		/// <summary>
		/// No Need to recompute the Assembly of the structure if the geometry has not changed. A geometry only consist in Nodes coordinates, ElementsEndNodes, IsDOFfree.
		/// </summary>
		/// <param name="obj"></param>
		/// <returns></returns>
		public bool HasSameGeometryThan(object obj)
		{
			//Check for null and compare run-time types.
			if ((obj == null) || !this.GetType().Equals(obj.GetType()))
			{
				return false;
			}
			SharedData other = (SharedData)obj;

			if (this.NodesCoord.Count != other.NodesCoord.Count) return false;
			for (int i = 0; i < NodesCoord.Count; i++)
			{
				for (int j = 0; j < 3; j++)
				{
					double double1 = this.NodesCoord[i][j];
					double double2 = other.NodesCoord[i][j];
					double difference = Math.Abs(double1 / 1e5);// Define the tolerance for variation in their values
					if (Math.Abs(double1 - double2) > difference) return false;
				}
			}

			if (this.ElementsEndNodes.Count != other.ElementsEndNodes.Count) return false;
			for (int i = 0; i < ElementsEndNodes.Count; i++)
			{
				for (int j = 0; j < 2; j++)
				{
					if (ElementsEndNodes[i][j] != other.ElementsEndNodes[i][j]) return false;
				}
			}
			if (this.IsDOFfree.Count != other.IsDOFfree.Count) return false;
			for (int i = 0; i < IsDOFfree.Count; i++)
			{
				if (IsDOFfree[i] != other.IsDOFfree[i]) return false;
			}

			return true;
		}

		private void RegisterElements(StructureObj structObj)
		{
			foreach (Element e in structObj.StructuralElements)
			{
				double AInComp = Math.Round(e.CS_Comp.Area * 1e6, 5);//Python works in mm² - and C# works in m²
				double AInTens = Math.Round(e.CS_Tens.Area * 1e6, 5);
				List<double> A = new List<double>() { AInComp, AInTens };
				double EInComp = Math.Round(e.Mat_Comp.E / 1e6, 5);//Python works in MPa² - C# works in Pa 
				double EInTens = Math.Round(e.Mat_Tens.E / 1e6, 5);
				List<double> E = new List<double>() { EInComp, EInTens };
				double Tension = Math.Round(e.Tension, 5); //Python and C# works in N
				double LFree = Math.Round(e.LFree, 8); //Python and C# works in m
				double LengtheningToApply = Math.Round(structObj.LengtheningsToApply[e.Ind], 8); //Python and C# works in m

				ElementsType.Add(e.Type);
				ElementsEndNodes.Add(e.EndNodes);
				ElementsA.Add(A);
				ElementsE.Add(E);
				TensionInit.Add(Tension);
				ElementsLFreeInit.Add(LFree);
				LengtheningsToApply.Add(LengtheningToApply);
			}
		}
		private void RegisterNodes(StructureObj structObj)
		{
			//			public List<List<double>> NodesCoord { get; set; } //shape (NodesCount, 3)
			//public List<List<double>> LoadsInit { get; set; } //shape (NodesCount, 3)
			//public List<List<double>> LoadsToApply { get; set; } //shape (NodesCount, 3)
			foreach (Node n in structObj.StructuralNodes)
			{
				double X = Math.Round(n.Point.X, 8); //Python works in m - C# works in m
				double Y = Math.Round(n.Point.Y, 8);
				double Z = Math.Round(n.Point.Z, 8);
				List<double> coord = new List<double>() { X, Y, Z };
				NodesCoord.Add(coord);

				IsDOFfree.Add(n.isXFree);
				IsDOFfree.Add(n.isYFree);
				IsDOFfree.Add(n.isZFree);

				double FInitx = Math.Round(n.Load.X, 5); //Python works in N - C# works in N
				double FInity = Math.Round(n.Load.Y, 5);
				double FInitz = Math.Round(n.Load.Z, 5);
				List<double> FInit = new List<double>() { FInitx, FInity, FInitz };
				LoadsInit.Add(FInit);

				double Fx = Math.Round(structObj.LoadsToApply[n.Ind].X, 5); //Python works in N - C# works in N
				double Fy = Math.Round(structObj.LoadsToApply[n.Ind].Y, 5);
				double Fz = Math.Round(structObj.LoadsToApply[n.Ind].Z, 5);
				List<double> F = new List<double>() { Fx, Fy, Fz };
				LoadsToApply.Add(F);

				double Rx = Math.Round(n.Reaction.X, 5); //Python works in N - C# works in N
				double Ry = Math.Round(n.Reaction.Y, 5);
				double Rz = Math.Round(n.Reaction.Z, 5);
				if (n.isXFree == false) ReactionsInit.Add(Rx); //add the reaction if the X dof is fixed
				if (n.isYFree == false) ReactionsInit.Add(Ry);
				if (n.isZFree == false) ReactionsInit.Add(Rz);

			}
		}

		private void RegisterDRMethodParameters(DRMethod dr)
		{
			Dt = dr.Dt;
			AmplMass = dr.AmplMass;
			MinMass = dr.MinMass;
			MaxTimeStep = dr.MaxTimeStep;
			MaxKEReset = dr.MaxKEReset;
		}
		#endregion Methods

	}
}