

namespace MuscleCore.TwinModel
{
	public class TwinElementsResults
	{
		#region Properties

		public double[] Tension { get; set; } //[N] - shape (ElementsCount,)
		public double[] ElasticElongation { get; set; } //[m] - shape (ElementsCount,)

		#endregion Properties

		#region Constructors
		public TwinElementsResults()
		{
			Tension = new double[] { };
			ElasticElongation = new double[] { };
		}
		#endregion Constructors
	}
}
