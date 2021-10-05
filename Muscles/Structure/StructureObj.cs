using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscles.Elements;
using Muscles.Nodes;
using Muscles.PythonLink;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles.Structure
{

	public class StructureObj
    {
		private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);

		#region Properties

		public string TypeName { get { return "Structure"; } }

		public List<string> warnings;

		public bool IsValid
		{
			get
			{
				return true;
			}
		}


		///// Geometric informations /////
		public double SpanX { get; set; }
		public double SpanY { get; set; }
		public double SpanZ { get; set; }
		public double ZeroTol { get; set; }

		///// Structure informations /////
		public int ElementsCount { get { return Struct_Elements.Count; } }
		public List<Element> Struct_Elements { get; set; }
		public int NodesCount { get { return Struct_Nodes.Count; } }
		public List<Node> Struct_Nodes { get; set; }
		public int FixationsCount { get { return Struct_Nodes.Select(n => n.FixationsCount).Sum(); } }
		public int DOFfreeCount { get { return 3*NodesCount-FixationsCount; } }

		///// Results coming from Python /////
		public SharedAssemblyResult AssemblyResult { get; set; }


		#endregion Properties

		#region Constructors


		/// <summary>
		/// Initialize all Properties
		/// </summary>
		private void Init()
        {
			warnings = new List<string>();

			SpanX = 0;
			SpanY = 0;
			SpanZ = 0;
			ZeroTol = 1e-5f; //(m)

			Struct_Elements = new List<Element>();
			Struct_Nodes = new List<Node>();

			AssemblyResult = new SharedAssemblyResult();

		}


		/// <summary>
		/// Default constructor
		/// </summary>
		public StructureObj()
        {
			Init();
        }

		public StructureObj(GH_Structure<IGH_Goo> GH_elements_input, GH_Structure<GH_Point> GH_points_input, GH_Structure<IGH_Goo> GH_supports_input)

		{
			Init();

			//1) Struct_Elements property is filled
			RegisterElements(GH_elements_input);

			//2) check validity of points inputs
			RegisterPointsAsNodes(GH_points_input);

			//3)
			RegisterNodesAsElementsExtremities();

			//4) check validity of supports inputs
			RegisterSupports(GH_supports_input);

		}

		public StructureObj(StructureObj other)
		{
			this.warnings = new List<string>();

			this.SpanX = other.SpanX;
			this.SpanY = other.SpanY;
			this.SpanZ = other.SpanZ;
			this.ZeroTol = other.ZeroTol; //(m)

			Struct_Elements = new List<Element>();
			foreach (Element e in other.Struct_Elements) Struct_Elements.Add(e.Duplicate());
			Struct_Nodes = new List<Node>();
			foreach (Node n in other.Struct_Nodes) Struct_Nodes.Add(n.Duplicate());
		}

		public StructureObj Duplicate() //Duplication method calling the copy constructor
		{
			return new StructureObj(this);
		}

		public StructureObj Deformed()
        {
			StructureObj deformed = this.Duplicate();
			foreach (Node n in deformed.Struct_Nodes)
            {
				int final = n.Displacement_Results.Count - 1; 
				if(final>=0)
                {
					Vector3d d = n.Displacement_Results[final];
					n.Point += d;           //update nodes coordinates
					n.Displacement_Already_Applied += d; // allows to keep track of the original position of the node

					n.Reaction_Already_Applied += n.Reaction_Results[final]; //not really a usefull information
					n.Load_Already_Applied += n.Load_Results[final]; //not really a usefull information
				}
            }
			foreach (Element e in deformed.Struct_Elements)
			{
				int final = e.AxialForce_Results.Count - 1;
				if (final >= 0)
				{
					double t = e.AxialForce_Results[final];
					e.AxialForce_Already_Applied += t; // allows to keep track of the original position of the node
				}

				//update the lines extremities
				int n0 = e.ExtremitiesIndex[0]; 
				int n1 = e.ExtremitiesIndex[1];
				Point3d p0 = deformed.Struct_Nodes[n0].Point;
				Point3d p1 = deformed.Struct_Nodes[n1].Point;
				e.Line = new Line(p0, p1);
			}
			return deformed;
        }

		#endregion Constructors

		#region Methods	

		public override string ToString()
		{
			return $"Structure of {NodesCount} nodes, {ElementsCount} elements, {FixationsCount} fixed displacements.";
		}

		#region 1)RegisterElements

		/// <summary>
		/// Transform the user inputted elements into properly formatted datas and register them in the StructureObject.
		/// </summary>
		private void RegisterElements(GH_Structure<IGH_Goo> GH_elements_input)
		{
			int index = 0;
			foreach(var data in GH_elements_input.FlattenData())
            {
				if (data is GH_Element)
                {
					GH_Element gh_elem = data as GH_Element;
					Struct_Elements.Add(gh_elem.Value);
					gh_elem.Value.Ind = index;
					index++;
				}
            }
		}

		#endregion 1)RegisterElements

		#region 2)RegisterPointsAsNodes

		private void RegisterPointsAsNodes(GH_Structure<GH_Point> GH_points_input)
		{
			int ind_node = 0; 
			//1) find the points that are extremities of the elements
			List<Point3d> points_from_lines = ExtremitiesOfElements();
			SpanXYZ(points_from_lines); // set the main dimensions of the structure and set the zeroTolerance for point equality
			List<Point3d> points_from_lines_wo_d = Node.RemoveDuplicatedPoints(points_from_lines,ZeroTol); //remove points that are equal in order to keep only one instance


			//2) if user inputed a list of points : we want to use its indexation of the nodes
			List<GH_Point> list_GH_points_input = GH_points_input.FlattenData();
			if (!(list_GH_points_input == null || list_GH_points_input.Count == 0))// if user gave points as input.
			{
				List<Point3d> points_input = list_GH_points_input.Select(gh => gh.Value).ToList(); //this transform a GH_Structure<GH_Point> into a List<Point3d> (without for loop). First we flatten the GH_Structure into a List<GH_Point>. Then each GH_Point is converted into a Point3D by replacing it by its value. 

				//2.a) make sure the user list of points do not contains duplicated points
				List<Point3d> points_input_wo_d = Node.RemoveDuplicatedPoints(points_input,ZeroTol);
				if (points_input_wo_d.Count < points_input.Count) { warnings.Add("Some user inputted points were duplicates and have been removed. Indexation of points may be affected."); } //warn the user if there were duplicates

                //2.b) make sure all lines extremities are contained in the user list of points, if not add the missing extremity at the end of the user list of points
                UserPointsContainsAllExtremities(points_input_wo_d, points_from_lines_wo_d);

                //Register the user list of point (wo duplicates) into a list of Nodes
                foreach (Point3d p in points_input_wo_d)
				{
					Struct_Nodes.Add(new Node(p,ind_node));
					ind_node++;
				}
			}
			else 
			{
				foreach (Point3d p in points_from_lines_wo_d)
				{
					Struct_Nodes.Add(new Node(p, ind_node));
					ind_node++;
				}
			}// if user did not give points as input, register the lines extremities

		}

		/// <summary>
		/// Creates a List of Point3d that are the extremities of Struct_Elements. The duplicated points are not removed. 
		/// </summary>
		private List<Point3d> ExtremitiesOfElements()
		{
			List<Point3d> points = new List<Point3d>();
			foreach (Element e in Struct_Elements)
			{
				points.Add(e.Line.From);
				points.Add(e.Line.To);
			}
			return points;
		}

		/// <summary>
		/// Deduce the main dimensions (in the X,Y and Z directions) of the box containing the structure. Set the ZeroTol of the structure. Two points are considered equal if they are closer than ZeroTol. A structure of 1m span have a ZeroTol = 0.01mm.  
		/// </summary>
		private void SpanXYZ(List<Point3d> points_from_lines)
		{
			double minX = points_from_lines[0].X;
			double maxX = points_from_lines[0].X;
			double minY = points_from_lines[0].Y;
			double maxY = points_from_lines[0].Y;
			double minZ = points_from_lines[0].Z;
			double maxZ = points_from_lines[0].Z;
			double X;
			double Y;
			double Z;

			foreach (Point3d point in points_from_lines)
			{
				X = point.X;
				Y = point.Y;
				Z = point.Z;
				if (X < minX) { minX = X; }
				if (X > maxX) { maxX = X; }
				if (Y < minY) { minY = Y; }
				if (Y > maxY) { maxY = Y; }
				if (Z < minZ) { minZ = Z; }
				if (Z > maxZ) { maxZ = Z; }
			}
			SpanX = Math.Abs(maxX - minX);
			SpanY = Math.Abs(maxY - minY);
			SpanZ = Math.Abs(maxZ - minZ);
			ZeroTol = Math.Max(SpanX, Math.Max(SpanY, SpanZ)) / 100000; // geometry of 1m span have a ZeroTol = 0.01mm. Two points are considered equal if they are closer than ZeroTol. 
		}

		/// <summary>
		/// make sure all lines extremities are contained in the user list of points, if not add the missing extremity at the end of the user list of points
		/// </summary>
		/// <param name="points_user"></param>
		/// <param name="extremities"></param>
		/// <returns></returns>
		private void UserPointsContainsAllExtremities(List<Point3d> points_user, List<Point3d> extremities)
		{
			int ind;
			foreach (Point3d extremity in extremities)
			{
				if (!Node.EpsilonContains(points_user, extremity, ZeroTol, out ind))
				{
					points_user.Add(extremity); //thus we add it
					warnings.Add("Some line extremities were not contained in the user list of points. They have been added at the end of the user list of points");
				}
			}
			if (points_user.Count > extremities.Count) { warnings.Add("Some Points inputted by the user are not connected to the geometry"); }
		}


		#endregion 2)RegisterPointsAsNodes

		#region 3)RegisterNodesAsElementsExtremities

		/// <summary>
		/// Creates a List of Point3d that are the extremities of a List of Lines. Duplicates Points are removed. 
		/// The indexes of the extremities are stored in the matrice IndexLinesExtremities 
		/// </summary>
		private void RegisterNodesAsElementsExtremities()
		{
			Point3d n0;
			Point3d n1;

			foreach (Element e in Struct_Elements)
			{
				n0 = e.Line.From;
				n1 = e.Line.To;

				int ind0 = -1;
				int ind1 = -1;
				for (int j = 0; j < Struct_Nodes.Count; j++) // parcourir tous les noeuds et voir a quel index correspond les extrémités d'un élément
				{
					if (Struct_Nodes[j].Point.EpsilonEquals(n0, ZeroTol)) { ind0 = j; }
					if (Struct_Nodes[j].Point.EpsilonEquals(n1, ZeroTol)) { ind1 = j; }
				}
				e.ExtremitiesIndex = new List<int> { ind0, ind1 }; // Dans tous les cas, on enregistre l'index des noeuds n0 et n1 dans l'objet Element
			}
		}
		#endregion 3)RegisterNodesAsElementsExtremities

		#region 4)RegisterSupports
		private void RegisterSupports(GH_Structure<IGH_Goo> GH_supports_input)
		{
			foreach (var data in GH_supports_input.FlattenData())
			{
				int ind;
				if (data is GH_Support)
				{
					GH_Support gh_spt = (GH_Support)data;
					Support spt = gh_spt.Value;
					if (Node.EpsilonContains(Struct_Nodes, spt.Point, ZeroTol, out ind))
					{
						Struct_Nodes[ind].AddSupport(spt);
					}
					else
					{
						warnings.Add("A support is defined on a point which do not belong to the geometry. This support is ignored.");
					}
				}
				else
				{
					throw new InvalidDataException("Input is not a support");
				}
			}
			//finally reference the identity of each reaction to be able to retrieve the results
			int ind_spt = 0;
			foreach (Node node in Struct_Nodes)
			{
				if (!node.isXFree)
				{
					node.Ind_RX = ind_spt;
					ind_spt++;
				}
				if (!node.isYFree)
				{
					node.Ind_RY = ind_spt;
					ind_spt++;
				}
				if (!node.isZFree)
				{
					node.Ind_RZ = ind_spt;
					ind_spt++;
				}
			}
		}
            #endregion 4)RegisterSupports

            #region PopulateWithSolverResult
        public void PopulateWithSolverResult(SharedSolverResult answ)
        {
			if (answ == null)
            {
				log.Warn("Structure: FAILED to populate with RESULTS");
				return;
			}
				
				 
			int final = answ.Stages.Count-1;
			for(int e=0; e< Struct_Elements.Count;e++)
            {
				Element elem = Struct_Elements[e];

				//1) axialforce results
				double prev_tension = 0.0;
				int prev = elem.AxialForce_Total.Count - 1;
				if (prev >= 0) //if it is not the first time that the structure has been solved
				{
					prev_tension = elem.AxialForce_Total[prev];
				}
				double Fpre = elem.AxialForce_To_Apply; //internal PrestressLoad

				List<double> Tension_Results = new List<double>();
				List<double> Tension_Total = new List<double>();
				for (int k = 0; k < answ.Stages.Count; k++) //for each iteration of the solver, register the solver results and the total results (sum with previous result)
				{
					double Tension = answ.AxialForces_Results[e][k] + Fpre; //Resulting force (from External Load and external PrestressLoad) is added to the pretension 
					Tension_Results.Add(Tension);
					Tension_Total.Add(prev_tension+Tension);
				}
				elem.AxialForce_To_Apply = 0.0; // reinitialize for next solve
				elem.AxialForce_Results = Tension_Results;
				elem.AxialForce_Total = Tension_Total; 

			}


			for (int n = 0; n < Struct_Nodes.Count; n++)
			{
				Node node = Struct_Nodes[n];

				// 1) Register the loads, the displacements, the reactions results from the solver
				Vector3d prev_load = new Vector3d();
				Vector3d prev_displ = new Vector3d();
				Vector3d prev_react = new Vector3d();

				int prev = node.Displacement_Total.Count - 1;
				if (prev >= 0) //if it is not the first time that the structure has been solved
				{
					prev_load = node.Load_Total[prev];
					prev_displ = node.Displacement_Total[prev];
					prev_react = node.Reaction_Total[prev];
				}

				List<Vector3d> Load_Results = new List<Vector3d>();
				List<Vector3d> Load_Total = new List<Vector3d>();
				List<Vector3d> Displ_Results = new List<Vector3d>();
				List<Vector3d> Displ_Total = new List<Vector3d>();
				List<Vector3d> React_Results = new List<Vector3d>();
				List<Vector3d> React_Total = new List<Vector3d>();

				for (int k = 0; k < answ.Stages.Count; k++) //for each iteration of the solver, register the solver results and the total results (sum with previous result)
				{
					//Register Loads Applied
					Vector3d Load = answ.Stages[k] * node.Load_To_Apply;
					Load_Results.Add(Load);
					Load_Total.Add(prev_load + Load);

					//Register Displacements Results
					double DisplX = answ.Displacements_Results[3 * n + 0][k];
					double DisplY = answ.Displacements_Results[3 * n + 1][k];
					double DisplZ = answ.Displacements_Results[3 * n + 2][k];
					Vector3d Displ = new Vector3d(DisplX, DisplY, DisplZ);
					Displ_Results.Add(Displ);
					Displ_Total.Add(prev_displ + Displ);

					//Register Reactions Results
					double ReactX = 0;
					double ReactY = 0;
					double ReactZ = 0;
					if (!node.isXFree) ReactX = answ.Reactions_Results[node.Ind_RX][k];
					if (!node.isYFree) ReactY = answ.Reactions_Results[node.Ind_RY][k];
					if (!node.isZFree) ReactZ = answ.Reactions_Results[node.Ind_RZ][k];
					Vector3d React = new Vector3d(ReactX, ReactY, ReactZ);
					React_Results.Add(React);
					React_Total.Add(prev_react + React);
				}

				//save the results (and overwrite the previous one)
				node.Load_Results = Load_Results;
				node.Load_Total = Load_Total;
				node.Displacement_Results = Displ_Results;
				node.Displacement_Total = Displ_Total;
				node.Reaction_Results = React_Results;
				node.Reaction_Total = React_Total;
				node.Load_To_Apply = new Vector3d(); //reinitialize for next solve
			}
			log.Info("Structure: Is well populated with RESULTS");
		}

		#endregion


		#endregion Methods
	}
}
