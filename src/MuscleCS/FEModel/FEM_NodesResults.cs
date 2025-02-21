

namespace MuscleCore.FEModel
{
	public class FEM_NodesResults
	{
		public double[,] Displacements { get; set; }  //[m] - shape (NodesCount,3)

		public double[,] Residual { get; set; } //[N] - shape (NodesCount,3)
		public double [,] Reactions { get; set; } //[N] - shape (NodesCount,3)

		public FEM_NodesResults()
		{
			Displacements = new double[,] { };
			Residual = new double[,] { };
			Reactions = new double[,] { };
		}
	}
}