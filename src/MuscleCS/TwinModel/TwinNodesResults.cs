

namespace MuscleCore.TwinModel
{
	public class TwinNodesResults
	{
		public double[,] Displacements { get; set; }  //[m] - shape (NodesCount,3)

		public double[,] Residual { get; set; } //[N] - shape (NodesCount,3)
		public double [,] Reactions { get; set; } //[N] - shape (NodesCount,3)

		public TwinNodesResults()
		{
			Displacements = new double[,] { };
			Residual = new double[,] { };
			Reactions = new double[,] { };
		}
		public TwinNodesResults(double[,] displacements, double[,] residual, double[,] reactions)
		{
			Displacements = displacements;
			Residual = residual;
			Reactions = reactions;
		}
	}
}