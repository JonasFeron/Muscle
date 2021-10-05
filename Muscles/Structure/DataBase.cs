using Muscles.Elements;
using Muscles.Nodes;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles.Structure
{
    public class DataBase
    {
		#region Properties

		public string TypeName { get { return "DataBase"; } }

		public bool IsValid
		{
			get
			{
				return true;
			}
		}



		///// Structure informations /////
		#region Nodes
		public int NodesCount { get { return NodesCoord0.Count; } }
		public List<List<double>> NodesCoord0 { get; set; } //shape (NodesCount, 3)
		#endregion Nodes


		#region Elements
		public int ElementsCount { get { return Elements_ExtremitiesIndex.Count; } }
		public List<List<int>> Elements_ExtremitiesIndex { get; set; } //shape (ElementsCount, 2)
		public List<List<int>> C { get; set; } //Connectivity matrix shape (ElementsCount, NodesCount) (contains the same info as ElementsExtremitiesIndex but arranged differently)
		public List<double> Elements_L0 { get; set; } //shape (ElementsCount) , Initial length of the element in meter
		public List<double> Elements_Cos_X { get; set; } //shape (ElementsCount) 
		public List<double> Elements_Cos_Y { get; set; } //shape (ElementsCount) 
		public List<double> Elements_Cos_Z { get; set; } //shape (ElementsCount) 

		public List<double> Elements_A { get; set; } //Area in m2 of the Elements
		public List<double> Elements_E { get; set; } //Young Modulus in Pa of the Elements
		#endregion Elements


		#region Supports
		public int DOFfreeCount { get { return IsDOFfree.Select(dof => Convert.ToInt32(dof)).Sum(); } }
		public int FixationsCount { get { return 3* NodesCount - DOFfreeCount; } }
		public List<bool> IsDOFfree { get; set; } // //shape (NodesCount, 1). Each point i is associated to its X DOF (3i), Y DOF (3i+1), Z DOF (3i+2). Each DOF can be fixed (False) or free (True).
		#endregion Supports

		#region StructureAnalysis
		public List<List<double>> K { get; set; } //stiffness matrix. shape (3NodesCount,3NodesCount)
		public List<List<double>> K_free { get; set; } //stiffness matrix. shape (DOFfreeCount,DOFfreeCount)
		public List<List<double>> A { get; set; } //equilibrium matrix. shape (3NodesCount, ElementsCount)
		public List<List<double>> A_free { get; set; } //equilibrium matrix. shape (DOFfreeCount, ElementsCount)
		public List<double> S { get; set; } // eigenvalues of the equilibrium matrix A_free
		public int r { get { return Sr.Count; } } //rank of the equilibrium matrix
		public List<double> Sr { get; set; } // non null eigenvalues of the equilibrium matrix A_free

		public int s { get { return SS.Count; } } // number of self-stress modes
		public List<List<double>> Vr_t { get; set; } //shape (r, ElementsCount) Interprétations: Bar tensions in equilibrium with Lambda*Loads of U_r  OR Bar elongations compatible with 1/Lambda * Extensional displacements of U_r
		public List<List<double>> Vs_t { get; set; } //shape (r, ElementsCount) Interprétations: Bar tensions in equilibrium with Lambda*Loads of U_r  OR Bar elongations compatible with 1/Lambda * Extensional displacements of U_r

		public List<List<double>> SS { get; set; } //self-stress modes. shape (s, ElementsCount)

		public int m { get { return Um_t_free.Count; } } // number of mechanisms 
		public List<List<double>> Ur_t { get; set; } // shape (r, 3NodesCount). Interprétations: Loads which can be equilibrated in the initial structure OR Extensional displacements
		public List<List<double>> Ur_t_free { get; set; } // shape (r, DOFfreeCount)
		public List<List<double>> Um_t { get; set; } // mechanisms. shape (m, 3NodesCount). Interprétations : Loads which can not be equilibrated in the initial structure OR Inextensional displacements (sol of B@d = 0)
		public List<List<double>> Um_t_free { get; set; } // mechanisms. shape (m, DOFfreeCount)
		#endregion StructureAnalysis


		///// Results informations /////



		#endregion Properties

		#region Constructors


		/// <summary>
		/// Initialize all Properties
		/// </summary>
		private void Init()
		{
			NodesCoord0 = new List<List<double>>();
			Elements_ExtremitiesIndex= new List<List<int>>();
			C = new List<List<int>>();
			Elements_L0 = new List<double>();
			Elements_Cos_X = new List<double>();
			Elements_Cos_Y = new List<double>();
			Elements_Cos_Z = new List<double>();
			Elements_A = new List<double>();
			Elements_E = new List<double>();

			IsDOFfree = new List<bool>();


			K = new List<List<double>>();
			K_free = new List<List<double>>();
			A = new List<List<double>>();
			A_free = new List<List<double>>();
			S = new List<double>();
			Sr = new List<double>();
			Vr_t = new List<List<double>>();
			Vs_t = new List<List<double>>();
			SS = new List<List<double>>();
			Ur_t = new List<List<double>>();
			Ur_t_free = new List<List<double>>();
			Um_t = new List<List<double>>();
			Um_t_free = new List<List<double>>();
		}


		/// <summary>
		/// Default constructor
		/// </summary>
		public DataBase()
		{
			Init();
		}

		public DataBase(StructureObj struct_obj)
		{
			Init();

			//1) 
			RegisterElements(struct_obj); 

			//2) 
			RegisterNodes(struct_obj);
		}



		#endregion Constructors


		#region Methods
		private void RegisterElements(StructureObj struct_obj)
		{
			foreach (Element e in struct_obj.Struct_Elements)
			{
				Elements_ExtremitiesIndex.Add(e.ExtremitiesIndex);
				Elements_L0.Add(e.Length);
				Elements_Cos_X.Add((double)e.Line.UnitTangent.X);
				Elements_Cos_Y.Add((double)e.Line.UnitTangent.Y);
				Elements_Cos_Z.Add((double)e.Line.UnitTangent.Z);
				Elements_A.Add(e.CS_Main.Area);
				Elements_E.Add(e.Mat_Main.E);
			}
		}
		private void RegisterNodes(StructureObj struct_obj)
		{
			foreach (Node n in struct_obj.Struct_Nodes)
			{
				List<double> coord = new List<double>() { (double)n.Point.X, (double)n.Point.Y, (double)n.Point.Z };
				NodesCoord0.Add(coord);

				IsDOFfree.Add(n.isXFree);
				IsDOFfree.Add(n.isYFree);
				IsDOFfree.Add(n.isZFree);
			}
		}
		#endregion Methods

	}
}
