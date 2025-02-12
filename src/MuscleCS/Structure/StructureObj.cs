using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.Elements;
using Muscle.Nodes;
//using Muscle.Solvers;
//using Muscle.Dynamics;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Muscle.Loads;
using Muscle.Supports;
using Muscle.PythonLink;

namespace Muscle.Structure
{

	public class StructureObj
	{

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
		public int ElementsCount { get { return StructuralElements.Count; } }
		public List<Element> StructuralElements { get; set; }
		public int NodesCount { get { return StructuralNodes.Count; } }
		public List<Node> StructuralNodes { get; set; }
		public int FixationsCount { get { return StructuralNodes.Select(n => n.FixationsCount).Sum(); } }
		public int DOFfreeCount { get { return 3 * NodesCount - FixationsCount; } }

		///// Data to send to Python /////
		public double Residual0Threshold { get; set; }

		public List<Vector3d> LoadsToApply { get; set; } // [N] - shape (NodesCount,) - the list of Loads to apply on each node of the structure

		public List<double> LengtheningsToApply { get; set; } // [m] - shape (ElementsCount,) - the list of lengthenings to apply on each element of the structure


		///// Results coming from Python /////

		public bool IsInEquilibrium { get; set; }

		//public DRMethod DR { get; set; }

		///public DynMethod DS { get; set; }
		///
		


		///Data used the dynamics computation
		public int NumberOfFrequency { get; set; } 
		//Contains the number of frequency/mode of the structure who are computed


		public List<double> Frequency { get; set; }
		public List<List<double>> Mode { get; set; }
		public List<List<Vector3d>> ModeVector { get; set; } //Modes written in a vector form
		public List<double> DynMass { get; set; } //Masses used for the dynamic computation
		//List containing on each position the mass [kg]. The position in the list is equal to the node index of the node on wich the mass is applied.
		public List<GH_PointLoad> PointMasses { get; set; } //Masses used for the dynamic computation in objects
		//The mass written in a list of point masses

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

			StructuralElements = new List<Element>();
			StructuralNodes = new List<Node>();

			Residual0Threshold = 0.0001;
			LoadsToApply = new List<Vector3d>();
			LengtheningsToApply = new List<double>();


			//DR = new DRMethod();

			////DYN
			//NumberOfFrequency = 0; 
			//Frequency = new List<double>();	
			//Mode = new List<List<double>>();
			//ModeVector = new List<List<Vector3d>> ();
			//DynMass = new List<double>();
			//PointMasses = new List<GH_PointLoad> ();
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

			//1) StructuralElements property is filled
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

			StructuralElements = new List<Element>();
			foreach (Element e in other.StructuralElements) StructuralElements.Add(e.Duplicate());

			StructuralNodes = new List<Node>();
			foreach (Node n in other.StructuralNodes) StructuralNodes.Add(n.Duplicate());

			Residual0Threshold = other.Residual0Threshold;

			LoadsToApply = other.LoadsToApply; // do not fill with old value
			LoadsToApply = new List<Vector3d>();
			foreach (var node in StructuralNodes) LoadsToApply.Add(new Vector3d(0.0, 0.0, 0.0)); // initialize the LoadsToApply vector with 0 load for each DOF. 

			//LengtheningsToApply = other.LengtheningsToApply;
			LengtheningsToApply = new List<double>();
			foreach (var elem in StructuralElements) LengtheningsToApply.Add(0.0); // initialize the LengtheningsToApply vector with 0m length change for each element. 


			//DR = other.DR.Duplicate();
			
		}

		public StructureObj Duplicate() //Duplication method calling the copy constructor
		{
			return new StructureObj(this);
		}


		#endregion Constructors

		#region Methods	

		public override string ToString()
		{
			return $"Structure of {NodesCount} nodes, {ElementsCount} elements, {FixationsCount} fixed displacements and the {NumberOfFrequency} first frequency(ies)(on {DOFfreeCount}).";
		}

		#region 1)RegisterElements

		/// <summary>
		/// Transform the user inputted elements into properly formatted datas and register them in the StructureObject.
		/// </summary>
		private void RegisterElements(GH_Structure<IGH_Goo> GH_elements_input)
		{
			int index = 0;
			foreach (var data in GH_elements_input.FlattenData())
			{
				if (data is GH_Element)
				{
					GH_Element gh_elem = data as GH_Element;
					StructuralElements.Add(gh_elem.Value);
					gh_elem.Value.Ind = index;
					LengtheningsToApply.Add(0.0);
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
			List<Point3d> points_from_lines = ElementsEndPoints();
			SpanXYZ(points_from_lines); // set the main dimensions of the structure and set the zeroTolerance for point equality
			List<Point3d> points_from_lines_wo_d = Node.RemoveDuplicatedPoints(points_from_lines, ZeroTol); //remove points that are equal in order to keep only one instance


			//2) if user inputed a list of points : we want to use its indexation of the nodes
			List<GH_Point> list_GH_points_input = GH_points_input.FlattenData();
			if (!(list_GH_points_input == null || list_GH_points_input.Count == 0))// if user gave points as input.
			{
				List<Point3d> points_input = list_GH_points_input.Select(gh => gh.Value).ToList(); //this transform a GH_Structure<GH_Point> into a List<Point3d> (without for loop). First we flatten the GH_Structure into a List<GH_Point>. Then each GH_Point is converted into a Point3D by replacing it by its value. 

				//2.a) make sure the user list of points do not contains duplicated points
				List<Point3d> points_input_wo_d = Node.RemoveDuplicatedPoints(points_input, ZeroTol);
				if (points_input_wo_d.Count < points_input.Count) { warnings.Add("Some user inputted points were duplicates and have been removed. Indexation of points may be affected."); } //warn the user if there were duplicates

				//2.b) make sure all lines extremities are contained in the user list of points, if not add the missing extremity at the end of the user list of points
				UserPointsContainsAllExtremities(points_input_wo_d, points_from_lines_wo_d);

				//Register the user list of point (wo duplicates) into a list of Nodes
				foreach (Point3d p in points_input_wo_d)
				{
					StructuralNodes.Add(new Node(p, ind_node));
					ind_node++;
				}
			}
			else
			{
				foreach (Point3d p in points_from_lines_wo_d)
				{
					StructuralNodes.Add(new Node(p, ind_node));
					ind_node++;
				}
			}// if user did not give points as input, register the lines extremities
			for (int i = 0; i < NodesCount; i++) LoadsToApply.Add(new Vector3d(0.0, 0.0, 0.0));
		}

		/// <summary>
		/// Creates a List of Point3d that are the extremities of StructuralElements. The duplicated points are not removed. 
		/// </summary>
		private List<Point3d> ElementsEndPoints()
		{
			List<Point3d> points = new List<Point3d>();
			foreach (Element e in StructuralElements)
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

			foreach (Element e in StructuralElements)
			{
				n0 = e.Line.From;
				n1 = e.Line.To;

				int ind0 = -1;
				int ind1 = -1;
				for (int j = 0; j < StructuralNodes.Count; j++) // parcourir tous les noeuds et voir a quel index correspond les extrémités d'un élément
				{
					if (StructuralNodes[j].Point.EpsilonEquals(n0, ZeroTol)) { ind0 = j; }
					if (StructuralNodes[j].Point.EpsilonEquals(n1, ZeroTol)) { ind1 = j; }
				}
				e.EndNodes = new List<int> { ind0, ind1 }; // Dans tous les cas, on enregistre l'index des noeuds n0 et n1 dans l'objet Element
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
					if (Node.EpsilonContains(StructuralNodes, spt.Point, ZeroTol, out ind))
					{
						StructuralNodes[ind].AddSupport(spt);
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
			foreach (Node node in StructuralNodes)
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

		//#region 5)RegisterDynamics

		///// <summary>
		///// Transform the user inputted elements into properly formatted datas and register them in the StructureObject.
		///// </summary>

		//#region PopulateWithSolverResult
		//public void PopulateWithSolverResult(SharedSolverResult answ)
		//{
		//	if (answ == null)
		//	{
		//		return;
		//	}
		//	IsInEquilibrium = answ.IsInEquilibrium;
		//	DR.nTimeStep = answ.nTimeStep;
		//	DR.nKEReset = answ.nKEReset;


		//	for (int n = 0; n < StructuralNodes.Count; n++)
		//	{
		//		Node node = StructuralNodes[n]; // lets give a nickname to the current node from the list. 

		//		// 1) Register the loads, the new nodescoordinates, the reactions results from the solver

		//		//Coordinates. 
		//		double X = answ.NodesCoord[n][0];
		//		double Y = answ.NodesCoord[n][1];
		//		double Z = answ.NodesCoord[n][2];
		//		node.Point = new Point3d(X, Y, Z);
		//		// NOTE that displacements can be simply computed in grasshopper as the vector between the old and the new coordinates


		//		//Loads
		//		double FX = answ.Loads[n][0];
		//		double FY = answ.Loads[n][1];
		//		double FZ = answ.Loads[n][2];
		//		node.Load = new Vector3d(FX, FY, FZ);

		//		//Residual
		//		double ResX = answ.Residual[n][0];
		//		double ResY = answ.Residual[n][1];
		//		double ResZ = answ.Residual[n][2];
		//		node.Residual = new Vector3d(ResX, ResY, ResZ);

		//		//Reactions 
		//		double ReactX = 0;
		//		double ReactY = 0;
		//		double ReactZ = 0;
		//		if (!node.isXFree) ReactX = answ.Reactions[node.Ind_RX];
		//		if (!node.isYFree) ReactY = answ.Reactions[node.Ind_RY];
		//		if (!node.isZFree) ReactZ = answ.Reactions[node.Ind_RZ];
		//		node.Reaction = new Vector3d(ReactX, ReactY, ReactZ);
		//	}


		//	for (int e = 0; e < StructuralElements.Count; e++)
		//	{
		//		Element elem = StructuralElements[e];

		//		//1) axialforce results
		//		elem.Tension = answ.Tension[e];
		//		elem.LFree = answ.ElementsLFree[e];

		//		//update the lines end points
		//		int n0 = elem.EndNodes[0];
		//		int n1 = elem.EndNodes[1];
		//		Point3d p0 = StructuralNodes[n0].Point; //make sure coordinates have been updated before the lines
		//		Point3d p1 = StructuralNodes[n1].Point;
		//		elem.Line = new Line(p0, p1);
		//	}

		//}

		//#endregion PopulateWithSolverResult
		////Use the result from the dynamic computation and set them in a structure object
		//public void PopulateWithSolverResult_dyn(SharedSolverResult answ)
		//{
		//	if (answ == null)
		//	{
		//		return;
		//	}
		//	NumberOfFrequency = answ.NumberOfFrequency;
		//	Frequency = answ.Frequency;
		//	Mode = answ.Modes;
		//	DynMass = answ.DynMasses;

		//}

		//#endregion PopulateWithSolverResult


		public GH_Structure<GH_Number> ListListToGH_Struct(List<List<double>> datalistlist)
		{
			GH_Path path;
			int i = 0;
			GH_Structure<GH_Number> res = new GH_Structure<GH_Number>();
			if(datalistlist ==null)
            {
				return res;
            }
			foreach (List<double> datalist in datalistlist)
			{
				path = new GH_Path(i);
				res.AppendRange(datalist.Select(data => new GH_Number(data)), path);
				i++;
			}
			return res;
		}

		//Display the List of List of Vector3D
		public GH_Structure<GH_Vector> ListListVectToGH_Struct(List<List<Vector3d>> datalistlist) 
		{
			GH_Path path;
			int i = 0;

			GH_Structure<GH_Vector> res = new GH_Structure<GH_Vector>();
			
			if (datalistlist == null)
			{
				return res;
			}
			foreach (List<Vector3d> datalist in datalistlist)
			{

				path = new GH_Path(i);
				res.AppendRange(datalist.Select(data => new GH_Vector(data)), path);
				i++;

			}
			return res;
		}

		#endregion Methods
	}
}

