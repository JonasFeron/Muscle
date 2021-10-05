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
    public class SharedSolverResult
    {
		#region Properties

		public string TypeName { get { return "SharedSolverResult"; } }


		#region Elements

		#endregion Elements


		#region Supports

		#endregion Supports

		#region StructureAnalysis
		public List<double> Stages { get; set; }
		public List<List<double>> AxialForces_Results { get; set; }
		public List<List<double>> Displacements_Results { get; set; }
		public List<List<double>> Reactions_Results { get; set; }

		#endregion StructureAnalysis


		///// Results informations /////



		#endregion Properties

		#region Constructors


		/// <summary>
		/// Initialize all Properties
		/// </summary>
		private void Init()
		{
			Stages = new List<double>();
			AxialForces_Results = new List<List<double>>();
			Displacements_Results = new List<List<double>>();
			Reactions_Results = new List<List<double>>();
		}


		/// <summary>
		/// Default constructor
		/// </summary>
		public SharedSolverResult()
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
