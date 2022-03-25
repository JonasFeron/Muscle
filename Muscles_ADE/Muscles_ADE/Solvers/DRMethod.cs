using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles_ADE.Solvers
{
    public class DRMethod
    {
        #region Properties

        #region MethodParameter
        public double Dt { get; set; } //[s] - scalar - the time step of the time incremental method
        public double AmplMass { get; set; } //[/] - scalar - the amplification factor of the mass in every DOF in case we run into convergence issue
        public double MinMass { get; set; } // [kg] - scalar - the min mass applied on every DOF
        public int MaxTimeStep { get; set; } // [/] - scalar - The maximum number of time increment before the method fails.
        public int MaxKEReset { get; set; } // [/] - scalar - The maximum number of reset of the Kinetic energy at the peaks before the method fails
        #endregion MethodParameter

        #region MethodResult
        public int nTimeStep { get; set; } // [/] - scalar - the number of time step such that t = nTimeStep * Dt

        public int nKEReset { get; set; } //  [/] - scalar - The number of time the Kinetic energy has been reset to 0 at the peaks during the method.

        #endregion MethodResult

        #endregion Properties

        #region Constructors
        public DRMethod()
        {
            Dt = 0.01;
            AmplMass = 1;
            MinMass = 0.005; //[kg]
            MaxTimeStep = 10000;
            MaxKEReset = 1000;
            nTimeStep = 0;
            nKEReset = 0;
        }
        public DRMethod(double dt, double amplMass, double minMass, int maxTimeStep, int maxKEReset)
        {
            Dt = dt;
            AmplMass = amplMass;
            MinMass = minMass; //[kg]
            MaxTimeStep = maxTimeStep;
            MaxKEReset = maxKEReset;
            nTimeStep = 0;
            nKEReset = 0;
        }

        public DRMethod(DRMethod other)
        {
            Dt = Dt;
            AmplMass = AmplMass;
            MinMass = MinMass;
            MaxTimeStep = MaxTimeStep;
            MaxKEReset = MaxKEReset;
            nTimeStep = nTimeStep;
            nKEReset = nKEReset;
        }

        public DRMethod Duplicate() //Duplication method calling the copy constructor
        {
            return new DRMethod(this);
        }
        #endregion Constructors

    }
}