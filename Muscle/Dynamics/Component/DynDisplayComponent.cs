using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Muscle.Nodes;
using Muscle.Dynamics;
using Rhino.Geometry;
using Muscle.Structure;
using Newtonsoft.Json;
using Muscle.PythonLink;

namespace Muscle.Dynamics
{
    public class DynDisplayComponent : GH_Component
    {

        private static readonly log4net.ILog log = LogHelper.GetLogger(System.Reflection.MethodBase.GetCurrentMethod().DeclaringType);
        #region Properties

        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
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
                    base("Dynamic Display", "DD", "Create the modal deformed structure considering the mode wanted by the user. The structure is deforming following the wanted node during the time.", "Muscles", "Dynamics")
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure who contains already the dynamic computation.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Mode", "Mode", "The mode that the user want to display.", GH_ParamAccess.item);
            pManager.AddNumberParameter("Amplitude", "Ampl.","Amplitude of the displacement of the mode.",GH_ParamAccess.item);
            pManager.AddNumberParameter("Frequency", "Freq.", "Frequency of the displacement of the mode.", GH_ParamAccess.item);
            pManager.AddIntegerParameter("Time increment", "Time increment", "Value variating with the time to display the mode.", GH_ParamAccess.item);

        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A modal deformed structure containing the total results.", GH_ParamAccess.item);
            //First return a list
            //pManager.AddGenericParameter("Wanted Mode", "Mode", "Mode who is asked by the user.", GH_ParamAccess.list);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            log.Info("Dynamic computation: NEW SOLVE INSTANCE");
            //1) Collect Data
            StructureObj structure = new StructureObj();
            int ModeUsedNumber = 1;
            int TimeIncrement = 1;
            double Amplitude = 1;
            double Freq = 1;
            //Obtain the data if the component is connected
            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetData(1, ref ModeUsedNumber)) { }
            if (!DA.GetData(2, ref Amplitude)) { }
            if (!DA.GetData(3, ref Freq)) { }
            if (!DA.GetData(4, ref TimeIncrement)) { } //Number of frequencies /mode that the user want to display

            StructureObj new_structure = structure.Duplicate(); // Duplicate the structure. The elements still contains the Initial Tension forces. The nodes are in their previously equilibrated coordinates with previous load already applied on it.

            //Add to the new structure the dynamic element
            // # of freq, freq and modes
            new_structure.NumberOfFrequency = structure.NumberOfFrequency;
            new_structure.Frequency = structure.Frequency;
            new_structure.Mode = structure.Mode;


            List<double> ModeUsed = new List<double>();
            ModeUsed = structure.Mode[ModeUsedNumber - 1];

            List<Vector3d> ModeUsedVector = new List<Vector3d>();
            int NumberOfNodes = structure.NodesCount;

            for (int i = 0; i < NumberOfNodes; i++) 
            {
                Vector3d ToAdd = new Vector3d();
                ToAdd.X = Amplitude*Math.Cos(Freq*TimeIncrement)*ModeUsed[i*3];
                ToAdd.Y = Amplitude*Math.Cos(Freq*TimeIncrement)*ModeUsed[i*3+1];
                ToAdd.Z = Amplitude*Math.Cos(Freq*TimeIncrement)*ModeUsed[i*3+2];
                ModeUsedVector.Add(ToAdd);
            }

            List<Vector3d> Coordinates = new List<Vector3d>();

            //Obtain the position of each Nodes
            foreach (Node n in structure.StructuralNodes)
            {
                Vector3d coord = new Vector3d();
                coord.X = Math.Round(n.Point.X, 8); //Python works in m - C# works in m
                coord.Y = Math.Round(n.Point.Y, 8);
                coord.Z = Math.Round(n.Point.Z, 8);
                Coordinates.Add(coord);

            }


            
            PopulateWithSolverResult_Mode( new_structure , Coordinates, ModeUsedVector);

            GH_StructureObj gh_structure = new GH_StructureObj(new_structure);
            //DA.SetDataList(0, ModeUsedVector);
            //DA.SetDataList(0, new_structure.StructuralNodes);
            DA.SetData(0, gh_structure);
        }


        
		public void PopulateWithSolverResult_Mode(StructureObj new_structure, List<Vector3d> Coordinates, List<Vector3d> ModeUsedVector)
		{


            for (int n = 0; n < new_structure.StructuralNodes.Count; n++)
            {
                Node node = new_structure.StructuralNodes[n]; // lets give a nickname to the current node from the list. 

                // 1) Register the new coordinates due to the mode

                //Coordinates. 
                double X = Coordinates[n].X + ModeUsedVector[n].X;
                double Y = Coordinates[n].Y + ModeUsedVector[n].Y;
                double Z = Coordinates[n].Z + ModeUsedVector[n].Z;
                node.Point = new Point3d(X, Y, Z);


            }
			log.Info("Structure: Is well populated with RESULTS");
		}
		
        #endregion Methods
    }
}
