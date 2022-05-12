using System;
using System.Collections.Generic;
using System.Linq;
using Muscle.Dynamics;
using System.Text;
using System.Threading.Tasks;

namespace Muscle
{
    public class DynData
    {
        #region Properties
        public string TypeName { get { return "Dynamics Data"; } }
        public int Index { get; set; } //index of the data
        //For the smallest frequence, the Ind equal 1 and then increases with the frequency 
        //The element is composed of Ind, the associated frequency and mode

        public double Freq { get; set; }
        public List<double> Mode { get; set; }


        /*
        public int FrequencyCount
        {
            get { return Math.Max(Ind); }
        }
        */

        #endregion Properties

        #region Constructors
        /// <summary>
        /// Initialize all properties to default value
        /// </summary>
        private void Init()
        {
            Index = -1;
            Freq = new int();
            Mode = new List<double>();

        }
        public DynData()
        {
            Init();
        }
        public DynData(double freq, List<double> mode)
        {
            Init();
            Freq = freq;
            Mode = mode;
        }

        public DynData(int positionNumber, double freq, List<double> mode)
        {
            Init();
            Index = positionNumber;
            Freq = freq;
            Mode = mode;
        }
        public DynData(DynData other)
        {
            Index = other.Index;
            Freq = other.Freq;
            Mode = other.Mode;

        }
        public DynData Duplicate() //Duplication method calling the copy constructor
        {
            return new DynData(this);
        }
        #endregion Constructors



        #region Methods

        public override string ToString()
        {
            return $"The dynamic data ordered at position {Index} correspond to a frequency of {Freq} with a mode {Mode}";
        }


        #endregion Methods
    }
}
