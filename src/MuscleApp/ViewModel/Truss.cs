using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using MuscleCore.FEModel;

namespace MuscleApp.ViewModel
{

    public class Truss
    {

        #region Properties

        public string TypeName { get { return "Structure"; } }

        /// <summary>
        /// List of warnings generated during structure initialization.
        /// </summary>
        public List<string> warnings { get; private set; }

        /// <summary>
        /// Absolute Tolerance for geometric comparisons in [m]. Two points are considered equal if they are closer than ZeroGeometricATol.
        /// This value is calculated based on the maximum structure's dimension/100,000.
        /// A 1m span structure has a ZeroGeometricATol of 0.01mm.
        /// </summary>
        public double ZeroGeometricATol { get; private set; }

        public bool IsValid
        {
            get { return true; }
        }

        ///// Structure informations /////
        public List<Element> Elements { get; set; }
        public List<Node> Nodes { get; set; }
        public int FixationsCount { get { return Nodes.Select(n => n.FixationsCount).Sum(); } }

        ///// Results coming from Python /////

        public bool IsInEquilibrium { get; set; }

        // public DRMethod DR { get; set; }

        ///public DynMethod DS { get; set; }
        ///



        ///Data used the dynamics computation
        // public int NumberOfFrequency { get; set; }
        // //Contains the number of frequency/mode of the structure who are computed


        // public List<double> Frequency { get; set; }
        // public List<List<double>> Mode { get; set; }
        // public List<List<Vector3d>> ModeVector { get; set; } //Modes written in a vector form
        // public List<double> DynMass { get; set; } //Masses used for the dynamic computation
        //                                           //List containing on each position the mass [kg]. The position in the list is equal to the node index of the node on wich the mass is applied.
        // public List<GH_PointMass> PointMasses { get; set; } //Masses used for the dynamic computation in objects
        //                                                     //The mass written in a list of point masses

        #endregion Properties

        #region Constructors


        /// <summary>
        /// Initialize all Properties
        /// </summary>
        private void Init()
        {
            warnings = new List<string>();

            ZeroGeometricATol = 1e-5f; //(m)

            Elements = new List<Element>();
            Nodes = new List<Node>();
            IsInEquilibrium = false;
            // Residual0Threshold = 0.0001;
            // LoadsToApply = new List<Vector3d>();
            // LengtheningsToApply = new List<double>();


            // DR = new DRMethod();

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
        public Truss()
        {
            Init();
        }

        /// <summary>
        /// Creates a Truss from lists of Elements, Points, and Supports.
        /// This constructor allows creating a structure without depending on Grasshopper types.
        /// </summary>
        /// <param name="elements">List of Element objects defining the structural elements</param>
        /// <param name="points">List of Point3d objects defining node locations</param>
        /// <param name="supports">List of Support objects defining boundary conditions</param>
        public Truss(List<Element> elements, List<Point3d> points, List<Support> supports)
        {
            Init();

            // Step 1: Register structural elements
            // This populates the Elements collection with Element instances
            RegisterElements(elements);

            // Step 2: Register points as nodes
            // This creates Node instances from input points, calculates structure dimensions,
            // and ensures all element endpoints are represented as nodes
            RegisterPointsAsNodes(points);

            // Step 3: Connect nodes to element endpoints
            // This establishes the topological relationship between elements and nodes
            RegisterNodesAsElementsEnds();

            // Step 4: Apply support conditions to nodes
            // This adds boundary conditions (fixed/free DOFs) to the appropriate nodes
            RegisterSupports(supports);
        }

        public Truss(Truss other)
        {
            warnings = new List<string>();

            ZeroGeometricATol = other.ZeroGeometricATol; //(m)

            Elements = new List<Element>();
            foreach (Element e in other.Elements) Elements.Add(e.Copy());

            Nodes = new List<Node>();
            foreach (Node n in other.Nodes) Nodes.Add(n.Copy());

            IsInEquilibrium = other.IsInEquilibrium;

            // Residual0Threshold = other.Residual0Threshold;

            // LoadsToApply = other.LoadsToApply; // do not fill with old value
            // LoadsToApply = new List<Vector3d>();
            // foreach (var node in Nodes) LoadsToApply.Add(new Vector3d(0.0, 0.0, 0.0)); // initialize the LoadsToApply vector with 0 load for each DOF. 

            // //LengtheningsToApply = other.LengtheningsToApply;
            // LengtheningsToApply = new List<double>();
            // foreach (var elem in Elements) LengtheningsToApply.Add(0.0); // initialize the LengtheningsToApply vector with 0m length change for each element. 


            // DR = other.DR.Duplicate();

        }

        public Truss Copy() //Duplication method calling the copy constructor
        {
            return new Truss(this);
        }

        #endregion Constructors

        #region Methods	

        public override string ToString()
        {
            return $"Structure of {Nodes.Count} nodes, {Elements.Count} elements, {FixationsCount} fixed displacements and {3 * Nodes.Count - FixationsCount} free degrees of freedom.";
        }

        #region 1)RegisterElements

        /// <summary>
        /// Processes a list of elements and registers them in the structure.
        /// Each element is added to the Elements collection and assigned a unique index.
        /// </summary>
        /// <param name="elements">List of elements to register in the structure</param>
        private void RegisterElements(List<Element> elements)
        {
            int index = 0;
            foreach (var element in elements)
            {
                Elements.Add(element);
                element.Idx = index;
                index++;
            }
        }

        #endregion 1)RegisterElements

        #region 2)RegisterPointsAsNodes

        /// <summary>
        /// Creates Node instances from input points and element endpoints.
        /// This method:
        /// 1. Extracts all element endpoints
        /// 2. Calculates structure dimensions and zero tolerance
        /// 3. Removes duplicate points
        /// 4. Ensures all element endpoints are included in the node list
        /// 5. Creates Node instances with appropriate indices
        /// </summary>
        /// <param name="points">List of Point3d objects defining node locations</param>
        private void RegisterPointsAsNodes(List<Point3d> points)
        {
            int ind_node = 0;
            //1) find the points that are extremities of the elements
            List<Point3d> points_from_lines = ElementsEndPoints();
            SpanXYZ(points_from_lines); // set the main dimensions of the structure and set the zeroTolerance for point equality
            List<Point3d> points_from_lines_wo_d = Node.RemoveDuplicatedPoints(points_from_lines, ZeroGeometricATol); //remove points that are equal in order to keep only one instance


            //2) if user inputed a list of points : we want to use its indexation of the nodes
            if (!(points == null || points.Count == 0))// if user gave points as input.
            {
                //2.a) make sure the user list of points do not contains duplicated points
                List<Point3d> points_input_wo_d = Node.RemoveDuplicatedPoints(points, ZeroGeometricATol);
                if (points_input_wo_d.Count < points.Count) { warnings.Add("Some user inputted points were duplicates and have been removed. Indexation of points may be affected."); } //warn the user if there were duplicates

                //2.b) make sure all lines extremities are contained in the user list of points, if not add the missing extremity at the end of the user list of points
                UserPointsContainsAllExtremities(points_input_wo_d, points_from_lines_wo_d);

                //Register the user list of point (wo duplicates) into a list of Nodes
                foreach (Point3d p in points_input_wo_d)
                {
                    Nodes.Add(new Node(p, ind_node));
                    ind_node++;
                }
            }
            else
            {
                foreach (Point3d p in points_from_lines_wo_d)
                {
                    Nodes.Add(new Node(p, ind_node));
                    ind_node++;
                }
            }// if user did not give points as input, register the lines extremities
            // for (int i = 0; i < NodesCount; i++) LoadsToApply.Add(new Vector3d(0.0, 0.0, 0.0));
        }

        /// <summary>
        /// Creates a List of Point3d that are the extremities of StructuralElements. The duplicated points are not removed. 
        /// </summary>
        private List<Point3d> ElementsEndPoints()
        {
            List<Point3d> points = new List<Point3d>();
            foreach (Element e in Elements)
            {
                points.Add(e.Line.From);
                points.Add(e.Line.To);
            }
            return points;
        }

        /// <summary>
        /// Calculates the ZeroTol value based on the structure's dimensions.
        /// ZeroTol is set to 1/100,000 of the maximum span in any direction.
        /// Two points are considered equal if they are closer than ZeroTol.
        /// For a structure with 1m span, ZeroTol = 0.01mm.
        /// </summary>
        /// <param name="points_from_lines">List of points representing element endpoints</param>
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
            ZeroGeometricATol = Math.Max(Math.Abs(maxX - minX), Math.Max(Math.Abs(maxY - minY), Math.Abs(maxZ - minZ))) / 100000; // geometry of 1m span have a ZeroTol = 0.01mm. Two points are considered equal if they are closer than ZeroTol. 
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
                if (!Node.EpsilonContains(points_user, extremity, ZeroGeometricATol, out ind))
                {
                    points_user.Add(extremity); //thus we add it
                    warnings.Add("Some line extremities were not contained in the user list of points. They have been added at the end of the user list of points");
                }
            }
            if (points_user.Count > extremities.Count) { warnings.Add("Some Points inputted by the user are not connected to the geometry"); }
        }


        #endregion 2)RegisterPointsAsNodes

        #region 3)RegisterNodesAsElementsEnds

        /// <summary>
        /// Establishes the topological relationship between elements and nodes.
        /// For each element, this method:
        /// 1. Identifies the nodes that correspond to its endpoints
        /// 2. Stores the node indices in the element's EndNodes property
        /// 
        /// This creates the connectivity information needed for structural analysis.
        /// </summary>
        private void RegisterNodesAsElementsEnds()
        {
            Point3d n0;
            Point3d n1;

            foreach (Element e in Elements)
            {
                n0 = e.Line.From;
                n1 = e.Line.To;

                int ind0 = -1;
                int ind1 = -1;
                for (int j = 0; j < Nodes.Count; j++) // parcourir tous les noeuds et voir a quel index correspond les extrémités d'un élément
                {
                    if (Nodes[j].Coordinates.EpsilonEquals(n0, ZeroGeometricATol)) { ind0 = j; }
                    if (Nodes[j].Coordinates.EpsilonEquals(n1, ZeroGeometricATol)) { ind1 = j; }
                }
                e.EndNodes = new List<int> { ind0, ind1 }; // Dans tous les cas, on enregistre l'index des noeuds n0 et n1 dans l'objet Element
            }
        }
        #endregion 3)RegisterNodesAsElementsEnds

        #region 4)RegisterSupports
        /// <summary>
        /// Applies support conditions to nodes from a list of Support objects.
        /// For each support in the input:
        /// 1. Identifies the node that corresponds to the support point
        /// 2. Applies the support conditions (fixed/free DOFs) to the node
        /// 3. Adds warnings if supports are defined at points not in the structure
        /// 
        /// This establishes the boundary conditions needed for structural analysis.
        /// </summary>
        /// <param name="supports">List of Support objects defining boundary conditions</param>
        private void RegisterSupports(List<Support> supports)
        {
            foreach (var support in supports)
            {
                int ind;
                if (Node.EpsilonContains(Nodes, support.Point, ZeroGeometricATol, out ind))
                {
                    Nodes[ind].AddSupport(support);
                }
                else
                {
                    warnings.Add("A support is defined on a point which do not belong to the geometry. This support is ignored.");
                }
            }
        }
        #endregion 4)RegisterSupports

        //#region 5)RegisterDynamics

        /// <summary>
        /// Transform the user inputted elements into properly formatted datas and register them in the StructureObject.
        /// </summary>

       

        // #endregion PopulateWithSolverResult
        // //Use the result from the dynamic computation and set them in a structure object
        // public void PopulateWithSolverResult_dyn(SharedSolverResult answ)
        // {
        //     if (answ == null)
        //     {
        //         return;
        //     }
        //     NumberOfFrequency = answ.NumberOfFrequency;
        //     Frequency = answ.Frequency;
        //     Mode = answ.Modes;
        //     DynMass = answ.DynMasses;

        // }

        // //#endregion PopulateWithSolverResult


        // //Display the List of List of Vector3D
        // public GH_Structure<GH_Vector> ListListVectToGH_Struct(List<List<Vector3d>> datalistlist)
        // {
        //     GH_Path path;
        //     int i = 0;

        //     GH_Structure<GH_Vector> res = new GH_Structure<GH_Vector>();

        //     if (datalistlist == null)
        //     {
        //         return res;
        //     }
        //     foreach (List<Vector3d> datalist in datalistlist)
        //     {

        //         path = new GH_Path(i);
        //         res.AppendRange(datalist.Select(data => new GH_Vector(data)), path);
        //         i++;

        //     }
        //     return res;
        // }

        #endregion Methods
    }
}
