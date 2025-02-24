

namespace MuscleCore.FEModel
{
	public class FEM_Nodes
	{

		public double[,] Coordinates { get; private set; } //shape (NodesCount, 3)

		public bool[] IsDOFfree { get; private set; } // [bool] - shape (3NodesCount,). Each DegreeOfFreedom can be fixed (False) or free (True). Each point i is associated to its X DOF (3i), Y DOF (3i+1), Z DOF (3i+2). .


		public FEM_Nodes()
		{
			Coordinates = new double[0, 0];
			IsDOFfree = Array.Empty<bool>();
		}
		public FEM_Nodes(double[,] coordinates, bool[] isDofFree)
		{
			Coordinates = coordinates;
			IsDOFfree = isDofFree;
		}

        // public void RegisterNodes(StructureObj structObj)
		// {
		// 	int nodeCount = structObj.StructuralNodes.Count;
		// 	NodesCoord = new double[nodeCount, 3];
		// 	LoadsInit = new double[nodeCount, 3];
		// 	LoadsToApply = new double[nodeCount, 3];
		// 	IsDOFfree = new bool[3 * nodeCount];
		// 	ReactionsInit = new double[3 * nodeCount];
		// 	for (int i = 0; i < nodeCount; i++)
		// 	{
		// 		Node n = structObj.StructuralNodes[i];
				
		// 		// Coordinates (Python works in m - C# works in m)
		// 		NodesCoord[i, 0] = n.Point.X;
		// 		NodesCoord[i, 1] = n.Point.Y;
		// 		NodesCoord[i, 2] = n.Point.Z;

		// 		// DOF freedom
		// 		IsDOFfree[3 * i] = n.isXFree;
		// 		IsDOFfree[3 * i + 1] = n.isYFree;
		// 		IsDOFfree[3 * i + 2] = n.isZFree;

		// 		// Initial loads (Python works in N - C# works in N)
		// 		LoadsInit[i, 0] = n.Load.X;
		// 		LoadsInit[i, 1] = n.Load.Y;
		// 		LoadsInit[i, 2] = n.Load.Z;

		// 		// Loads to apply
		// 		LoadsToApply[i, 0] = structObj.LoadsToApply[n.Ind].X;
		// 		LoadsToApply[i, 1] = structObj.LoadsToApply[n.Ind].Y;
		// 		LoadsToApply[i, 2] = structObj.LoadsToApply[n.Ind].Z;

		// 		// Reactions
		// 		if (n.isXFree == false) ReactionsInit[3 * i] = n.Reaction.X; //add the reaction if the X dof is fixed
		// 		if (n.isYFree == false) ReactionsInit[3 * i + 1] = n.Reaction.Y;
		// 		if (n.isZFree == false) ReactionsInit[3 * i + 2] = n.Reaction.Z;
		// 	}
		// }
    }
}