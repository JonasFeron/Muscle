

namespace MuscleCore.FEModel
{
	public class FEM_ElementsResults
	{
		#region Properties

		public double[] Tension { get; set; } //[N] - shape (ElementsCount,)
		public double[] ElasticElongation { get; set; } //[m] - shape (ElementsCount,)

		#endregion Properties

		#region Constructors
		public FEM_ElementsResults()
		{
			Tension = new double[] { };
			ElasticElongation = new double[] { };
		}
		#endregion Constructors
	}
}
