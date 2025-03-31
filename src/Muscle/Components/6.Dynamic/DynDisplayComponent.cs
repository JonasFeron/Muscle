using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Rhino.Geometry;
using MuscleApp.ViewModel;
using Muscle.View;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Dynamic
{
    public class DynDisplayComponent : GH_Component
    {

        #region Properties

        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //return Properties.Resources.PLAY;
                return null;
            }
        }

        public override Guid ComponentGuid
        { 
            get { return new Guid("18cd1195aa3746c7a11dce0f889fa6e3"); } 
        }

        #endregion Properties

        #region Constructors

        public DynDisplayComponent() :
                    base("Dynamics Display", "DD", "Create the modal deformed structure considering the mode wanted by the user. The structure is deforming following the wanted node during the time.", "Muscles", "Dynamics")
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "Struct.", "A structure who contains already the dynamic computation.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Mode", "Mode", "The mode that the user want to display.(Begin at 1)", GH_ParamAccess.item);
            pManager.AddNumberParameter("Amplitude of the displayed displacement", "Displ. Ampl. Factor","Amplitude of the displacement of the mode.",GH_ParamAccess.item);
            pManager[2].Optional = true;
            pManager.AddNumberParameter("Circular frequency of the display", "Freq. ", "Circular frequency of the display. The display follows a cosine function as : cos(freq*Time increment)", GH_ParamAccess.item);
            pManager[3].Optional = true;
            pManager.AddIntegerParameter("Time increment", "Time Increment", "Value variating with the time to display the mode.", GH_ParamAccess.item);
            pManager[4].Optional = true;
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "Struct.", "A modal deformed structure containing the total results.", GH_ParamAccess.item);
           
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            //log.Info("Dynamic display : obtaining the data");

            //1) Collect Data
            StructureObj structure = new StructureObj();
            int ModeUsedNumber = 1;
            int TimeIncrement = 0;
            double Amplitude = 1;
            double Freq = 1;


            //Obtain the data if the component is connected
            //Some data are optionnal
            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetData(1, ref ModeUsedNumber)) { } //Number of mode that the user want to display
            if (!DA.GetData(2, ref Amplitude)) { }
            if (!DA.GetData(3, ref Freq)) { }
            if (!DA.GetData(4, ref TimeIncrement)) { }

            //2) Duplicate the structure. new_structure will be returned
            StructureObj new_structure = structure.Duplicate();
            // Duplicate the structure. The elements still contains the Initial Tension forces. The nodes are in their previously equilibrated coordinates with previous load already applied on it.


            //3) Change the node coordinates following some rules
            GH_StructureObj gh_structure = new GH_StructureObj(new_structure);

            //Add to the new structure the dynamic element
            // # of freq, freq and modes
            new_structure.NumberOfFrequency = structure.NumberOfFrequency;
            new_structure.Frequency = structure.Frequency;
            new_structure.Mode = structure.Mode;
            new_structure.DynMass = structure.DynMass;
            new_structure.ModeVector = structure.ModeVector;

            if (ModeUsedNumber < 1 ) //Need to be bigger than 1
            {
                
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "The listing of the modes begin at 1.");
                DA.SetData(0, gh_structure);
            }
            else
            {
                if(ModeUsedNumber > structure.NumberOfFrequency && ModeUsedNumber <= structure.DOFfreeCount) //Need to be a computed node
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "This mode is still not computed. Please modify the input of the 'Dynamic solver' component.");
                    DA.SetData(0, gh_structure);
                }
                else
                {
                    if ( ModeUsedNumber > structure.DOFfreeCount) //Problem if the index of the mode doesn't exist
                    {
                        AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"This mode doesn't exist. The maximum mode is {structure.DOFfreeCount}.");
                        DA.SetData(0, gh_structure);
                    }
                    else
                    {


                        //Mode that need to be displayed = ModeUsed
                        List<double> ModeUsed = new List<double>();
                        ModeUsed = structure.Mode[ModeUsedNumber - 1];


                        //Mode to display in a special shape : a list containing vectors(dx,dy,dz)
                        List<Vector3d> ModeUsedVector = new List<Vector3d>();
                        int NumberOfNodes = structure.NodesCount;

                        List<Node> NodesCoord = structure.StructuralNodes;
                        List<GH_PointMass> selfmass = new List<GH_PointMass>();

                        //For all nodes compute the variation of displacement due to the mode
                        for (int i = 0; i < NumberOfNodes; i++)
                        {
                            Vector3d ToAdd = new Vector3d();
                            ToAdd.X = Amplitude * Math.Cos(Freq * TimeIncrement) * ModeUsed[i * 3];
                            ToAdd.Y = Amplitude * Math.Cos(Freq * TimeIncrement) * ModeUsed[i * 3 + 1];
                            ToAdd.Z = Amplitude * Math.Cos(Freq * TimeIncrement) * ModeUsed[i * 3 + 2];
                            ModeUsedVector.Add(ToAdd);

                        }


                        List<Vector3d> Coordinates = new List<Vector3d>();

                        //Obtain the position of each Nodes
                        foreach (Node n in structure.StructuralNodes)
                        {
                            Vector3d coord = new Vector3d();
                            coord.X = Math.Round(n.Point.X, 8);
                            coord.Y = Math.Round(n.Point.Y, 8);
                            coord.Z = Math.Round(n.Point.Z, 8);
                            Coordinates.Add(coord);

                        }
                        


                        //Adapt the coordinates of all nodes
                        //Adapt the extremities of all elements
                        PopulateWithSolverResult_Mode(new_structure, Coordinates, ModeUsedVector);



                        //Adapt the coordinates of the point masses with the moving structure
                        foreach (GH_PointMass mass in structure.PointMasses)
                        {
                            int NodeIndex = mass.Value.NodeInd;
                            Point3d NewPoint = new_structure.StructuralNodes[NodeIndex].Point;


                            Vector3d Mass = new Vector3d();


                            Mass = mass.Value.Vector; //The 'mass' is saved in a point load element (vector shape)

                            PointMass DisplayMass = new PointMass(NodeIndex, NewPoint, Mass); //Point mass containing the new  coordinates

                            GH_PointMass p0 = new GH_PointMass(DisplayMass);
                            selfmass.Add(p0); //make a list

                        }
                        new_structure.PointMasses = selfmass; //the new_structure recieve a new list of point masses



                        //Return
                        new_structure.PointMasses = selfmass;

                        DA.SetData(0, gh_structure);
                    }
                }
            }
            
        }


        
		public void PopulateWithSolverResult_Mode(StructureObj new_structure, List<Vector3d> Coordinates, List<Vector3d> ModeUsedVector)
		{

            // 1) Register the new coordinates due to the mode
            for (int n = 0; n < new_structure.StructuralNodes.Count; n++)
            {
                Node node = new_structure.StructuralNodes[n]; // lets give a nickname to the current node from the list. 

                

  
                //Coordinates are adapted from the coordinate of the initial structure
                double X = Coordinates[n].X + ModeUsedVector[n].X;
                double Y = Coordinates[n].Y + ModeUsedVector[n].Y;
                double Z = Coordinates[n].Z + ModeUsedVector[n].Z;
                node.Point = new Point3d(X, Y, Z);


            }
			//log.Info("Dynamic display: new coordinates");


            // 2) Register the end-element node : Put up to date the element line of the structure
            for (int e = 0; e < new_structure.StructuralElements.Count; e++)
            {
                Element elem = new_structure.StructuralElements[e];


                //update the lines end points
                int n0 = elem.EndNodes[0];
                int n1 = elem.EndNodes[1];
                Point3d p0 = new_structure.StructuralNodes[n0].Point; //make sure coordinates have been updated before the lines
                Point3d p1 = new_structure.StructuralNodes[n1].Point;
                elem.Line = new Line(p0, p1);
            }
            //log.Info("Dynamic display: adapt the elements extremities");
        }
		
        #endregion Methods
    }
}
