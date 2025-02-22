namespace MuscleCore.TwinModel
{
	public class TwinActions
	{
		#region Properties

		public double[,] Loads { get; set; } = new double[0, 0]; //[N] - shape (NodesCount,3)
        public double[] Delta_FreeLengths { get; set; } = Array.Empty<double>(); //[m] - shape (ElementsCount,)

        #endregion Properties

        #region Constructors
        public TwinActions()
		{
			Loads = new double[,] { };
			Delta_FreeLengths = Array.Empty<double>();
		}
		public TwinActions(double[,] loads, double[] delta_FreeLengths)
        {
            Loads = loads;
            Delta_FreeLengths = delta_FreeLengths;
        }
        #endregion Constructors
    }
}