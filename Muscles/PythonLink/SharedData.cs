using Muscles.Elements;
using Muscles.Nodes;
using Muscles.Structure;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles.PythonLink
{
    public class SharedData
    {
		#region Properties

		public string TypeName { get { return "SharedData"; } }

		#region Nodes
		public List<List<double>> NodesCoord { get; set; } //shape (NodesCount, 3)
		public List<List<double>> Loads_To_Apply { get; set; }

		#endregion Nodes


		#region Elements
		public List<List<int>> Elements_ExtremitiesIndex { get; set; } //shape (ElementsCount, 2)
		public List<double> Elements_A { get; set; } //Area in mm² of the Elements
		public List<double> Elements_E { get; set; } //Young Modulus in MPa of the Elements

		public List<double> AxialForces_Already_Applied { get; set; }
		#endregion Elements


		#region Supports
		public List<bool> IsDOFfree { get; set; } // //shape (NodesCount, 1). Each point i is associated to its X DOF (3i), Y DOF (3i+1), Z DOF (3i+2). Each DOF can be fixed (False) or free (True).
		#endregion Supports

		public int n_steps { get; set; } // number of steps for the non-linear solver


		#endregion Properties

		#region Constructors


		/// <summary>
		/// Initialize all Properties
		/// </summary>
		private void Init()
		{
			n_steps = 1;
            NodesCoord = new List<List<double>>();
			Elements_ExtremitiesIndex= new List<List<int>>();
			Elements_A = new List<double>();
			Elements_E = new List<double>();
			AxialForces_Already_Applied = new List<double>();
			Loads_To_Apply = new List<List<double>>();

			IsDOFfree = new List<bool>();
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
		/// No Need to recompute the Assembly of the structure if the geometry has not changed. A geometry only consist in Nodes coordinates, Elements_Extrimities, IsDOFfree.
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
			for(int i=0; i< NodesCoord.Count; i++)
            {
				for (int j = 0; j < 3; j++)
                {
					double double1 = this.NodesCoord[i][j];
					double double2 = other.NodesCoord[i][j];
					double difference = Math.Abs(double1 / 1e5);// Define the tolerance for variation in their values
					if (Math.Abs(double1 - double2) > difference) return false;
				}
			}

			if (this.Elements_ExtremitiesIndex.Count != other.Elements_ExtremitiesIndex.Count) return false;
			for (int i = 0; i < Elements_ExtremitiesIndex.Count; i++)
			{
				for (int j = 0; j < 2; j++)
				{
					if (Elements_ExtremitiesIndex[i][j]!= other.Elements_ExtremitiesIndex[i][j]) return false;
				}
			}
			if (this.IsDOFfree.Count != other.IsDOFfree.Count) return false;
			for (int i = 0; i < IsDOFfree.Count; i++)
			{
				if (IsDOFfree[i] != other.IsDOFfree[i]) return false;
			}

			return true ;
		}

		private void RegisterElements(StructureObj structObj)
		{
			foreach (Element e in structObj.Struct_Elements)
			{
				double A = Math.Round(e.CS_Main.Area*1e6, 2); //Python works in mm² - and C# works in m²
				double E = Math.Round(e.Mat_Main.E/1e6, 2); //Python works in MPa² - C# works in Pa 
				double P = Math.Round(e.AxialForce_Already_Applied, 2); //Python and C# works in N

				Elements_ExtremitiesIndex.Add(e.ExtremitiesIndex);
				Elements_A.Add(A);
				Elements_E.Add(E);
				AxialForces_Already_Applied.Add(P);
			}
		}
		private void RegisterNodes(StructureObj structObj)
		{
			foreach (Node n in structObj.Struct_Nodes)
			{
				double X = Math.Round(n.Point.X, 5); //Python works in m - C# works in m
				double Y = Math.Round(n.Point.Y, 5);
				double Z = Math.Round(n.Point.Z, 5);
				List<double> coord = new List<double>() {X, Y, Z};
				NodesCoord.Add(coord);

				IsDOFfree.Add(n.isXFree);
				IsDOFfree.Add(n.isYFree);
				IsDOFfree.Add(n.isZFree);

				double Fx = Math.Round(n.Load_To_Apply.X, 2); //Python works in N - C# works in N
				double Fy = Math.Round(n.Load_To_Apply.Y, 2); 
				double Fz = Math.Round(n.Load_To_Apply.Z, 2); 
				List<double> F = new List<double>() { Fx, Fy, Fz };
				Loads_To_Apply.Add(F);
			}
		}
		#endregion Methods

	}
}
