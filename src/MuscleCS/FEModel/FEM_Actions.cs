namespace Muscle.FEModel
{
	public class FEM_Actions
	{
		#region Properties

		public double[,] Loads { get; set; } //[N] - shape (NodesCount,3)
		public double[] Delta_FreeLengths { get; set; } //[m] - shape (ElementsCount,)

		#endregion Properties

		#region Constructors
		public FEM_Actions()
		{
			Loads = new double[,] { };
			Delta_FreeLengths = new double[] { };
		}
		#endregion Constructors
	}
}