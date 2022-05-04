using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Muscle.Dynamics;

namespace Muscle.Dynamics
{
    public class DynMethod
    {
        #region Properties

        #region MethodParameter

        #endregion MethodParameter

        #region MethodResult

        #endregion MethodResult

        #region DynamicsComputation

        public double DynamicMass { get; set; } //[kg] - scalar - mass used for the dynamic computation

        #endregion DynamicsComputation

        #endregion Properties

        #region Constructors
        public DynMethod()
        {

            DynamicMass = 1; //[kg]

        }
        
        public DynMethod(double dynamicmass)
        {

            DynamicMass = dynamicmass; //[kg]

        }
        /*
        public DynMethod Duplicate() //Duplication method calling the copy constructor
        {
            return new DynMethod(this);
        } */
        #endregion Constructors
       
    }
}