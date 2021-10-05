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
    public class SharedAssemblyResult
    {
		#region Properties

		public string TypeName { get { return "SharedAssemblyResult"; } }


		#region Elements
		public List<List<int>> C { get; set; } //Connectivity matrix shape (ElementsCount, NodesCount) (contains the same info as ElementsExtremitiesIndex but arranged differently)

		#endregion Elements


		#region Supports

		#endregion Supports

		#region StructureAnalysis
		public List<List<double>> Km { get; set; } //stiffness matrix. shape (3NodesCount,3NodesCount)
		public List<List<double>> Km_free { get; set; } //stiffness matrix. shape (DOFfreeCount,DOFfreeCount)
		public List<List<double>> A { get; set; } //equilibrium matrix. shape (3NodesCount, ElementsCount)
		public List<List<double>> A_free { get; set; } //equilibrium matrix. shape (DOFfreeCount, ElementsCount)
		public List<double> S { get; set; } // eigenvalues of the equilibrium matrix A_free
		public int r { get; set; } //rank of the equilibrium matrix
		public List<double> Sr { get; set; } // non null eigenvalues of the equilibrium matrix A_free

		public int s { get; set; } // number of self-stress modes
		public List<List<double>> Vr_row { get; set; } //shape (r, ElementsCount) Interprétations: Bar tensions in equilibrium with Lambda*Loads of U_r  OR Bar elongations compatible with 1/Lambda * Extensional displacements of U_r
		public List<List<double>> Vs_row { get; set; } //shape (r, ElementsCount) Interprétations: Bar tensions in equilibrium with Lambda*Loads of U_r  OR Bar elongations compatible with 1/Lambda * Extensional displacements of U_r
		public List<List<double>> SS { get; set; } //self-stress modes. shape (s, ElementsCount)

		public int m { get; set; } // number of mechanisms 
		public List<List<double>> Ur_row { get; set; } // shape (r, 3NodesCount). Interprétations: Loads which can be equilibrated in the initial structure OR Extensional displacements
		public List<List<double>> Ur_free_row { get; set; } // shape (r, DOFfreeCount)
		public List<List<double>> Um_row { get; set; } // mechanisms. shape (m, 3NodesCount). Interprétations : Loads which can not be equilibrated in the initial structure OR Inextensional displacements (sol of B@d = 0)
		public List<List<double>> Um_free_row { get; set; } // mechanisms. shape (m, DOFfreeCount)
		#endregion StructureAnalysis


		///// Results informations /////



		#endregion Properties

		#region Constructors


		/// <summary>
		/// Initialize all Properties
		/// </summary>
		private void Init()
		{
			C = new List<List<int>>();
			Km = new List<List<double>>();
			Km_free = new List<List<double>>();
			A = new List<List<double>>();
			A_free = new List<List<double>>();
			S = new List<double>();
			Sr = new List<double>();
			Vr_row = new List<List<double>>();
			Vs_row = new List<List<double>>();
			SS = new List<List<double>>();
			Ur_row = new List<List<double>>();
			Ur_free_row = new List<List<double>>();
			Um_row = new List<List<double>>();
			Um_free_row = new List<List<double>>();
		}


		/// <summary>
		/// Default constructor
		/// </summary>
		public SharedAssemblyResult()
		{
			Init();
		}

		//public SharedAssemblyResult(StructureObj structObj)
		//{
		//	Init();
		//	RegisterElements(structObj); 
		//	RegisterNodes(structObj);
		//}

		#endregion Constructors

		#region Methods

		#endregion Methods

	}
}
