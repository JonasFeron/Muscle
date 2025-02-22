


namespace MuscleCore.TwinModel
{
	public class TwinElements
	{
		#region Properties

		public int[] Type { get; set; } //shape (ElementsCount, )
		public int[,] EndNodes { get; set; } //shape (ElementsCount, 2)
		public double[,] Areas { get; set; } // [mm²] - shape (ElementsCount, 2) - Area in Compression and Area in Tension of the Elements
		public double[,] YoungModuli { get; set; } // [MPa] - shape (ElementsCount, 2) - Young Modulus in Compression and in Tension of the Elements
		// public double[] Initial_FreeLengths { get; set; } //shape (ElementsCount, ) - Free Length of the Elements before any analysis

		#endregion

		#region Constructors
		public TwinElements()
		{
			Type = new int[] { };
			EndNodes = new int[,] { };
			Areas = new double[,] { };
			YoungModuli = new double[,] { };
			// Initial_FreeLengths = new double[] { };
		}

		#endregion Constructors


	}
}