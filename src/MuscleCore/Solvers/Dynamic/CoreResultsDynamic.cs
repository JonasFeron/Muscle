using System;

namespace MuscleCore.Solvers
{
    /// <summary>
    /// This class stores the results of the dynamic modal analysis of a structure.
    /// It contains natural frequencies and corresponding mode shapes for a structure
    /// with a given mass distribution and stiffness.
    /// </summary>
    public class CoreResultsDynamic
    {
        /// <summary>
        /// Natural frequencies in Hz
        /// </summary>
        public double[] Frequencies { get; private set; }

        /// <summary>
        /// Mode shapes corresponding to the natural frequencies
        /// </summary>
        public double[,] ModeShapes { get; private set; }

        /// <summary>
        /// A vector (3n) of Masses representing a simplified version of the Mass matrix for visualization purpose.
        /// the Mass matrix (3n,3n) was transformed into a vector (3n), by adding up the entries for each row.
        /// </summary>
        public double[] Masses { get; private set; }


        /// <summary>
        /// Empty constructor for deserialization
        /// </summary>
        public CoreResultsDynamic()
        {
            // Initialize with empty arrays to prevent null reference exceptions
            Frequencies = Array.Empty<double>();
            ModeShapes = new double[0, 0];
            Masses = Array.Empty<double>();
        }

        /// <summary>
        /// Initialize a CoreResultsDynamic object that stores the results of modal analysis.
        /// </summary>
        /// <param name="frequencies">Natural frequencies in Hz</param>
        /// <param name="modeShapes">Mode shapes corresponding to the natural frequencies</param>
        /// <param name="massMatrix">Mass matrix of the structure</param>
        public CoreResultsDynamic(double[] frequencies, double[,] modeShapes, double[] masses)
        {
            Frequencies = frequencies ?? throw new ArgumentNullException(nameof(frequencies));
            ModeShapes = modeShapes ?? throw new ArgumentNullException(nameof(modeShapes));
            Masses = masses ?? throw new ArgumentNullException(nameof(masses));
        }

        /// <summary>
        /// Number of computed modes
        /// </summary>
        public int ModeCount => Frequencies.Length;

        /// <summary>
        /// Angular frequencies in rad/s (ω = 2π·f)
        /// </summary>
        public double[] AngularFrequencies
        {
            get
            {
                double[] angularFrequencies = new double[Frequencies.Length];
                for (int i = 0; i < Frequencies.Length; i++)
                {
                    angularFrequencies[i] = 2 * Math.PI * Frequencies[i];
                }
                return angularFrequencies;
            }
        }

        /// <summary>
        /// Periods in seconds (T = 1/f)
        /// </summary>
        public double[] Periods
        {
            get
            {
                double[] periods = new double[Frequencies.Length];
                for (int i = 0; i < Frequencies.Length; i++)
                {
                    periods[i] = 1 / Frequencies[i];
                }
                return periods;
            }
        }
    }
}
