namespace MuscleCore.FEModel
{
	public class FEM_Actions
	{
		#region Properties

		public double[,] Loads { get; set; } = new double[0, 0]; //[N] - shape (NodesCount,3)
        public double[] Delta_FreeLengths { get; set; } = Array.Empty<double>(); //[m] - shape (ElementsCount,)

        #endregion Properties

        #region Constructors
        public FEM_Actions()
		{
			Loads = new double[,] { };
			Delta_FreeLengths = Array.Empty<double>();
		}
		public FEM_Actions(double[,] loads, double[] delta_FreeLengths)
        {
            Loads = loads;
            Delta_FreeLengths = delta_FreeLengths;
        }
        #endregion Constructors
    }
}