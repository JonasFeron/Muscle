using Rhino.Geometry;
namespace Muscle
{
    public static class MuscleConfig
    {

        #region Display
        public static double DisplaySupportAmpli = 1.0;
        //public static List<double> DisplaySupportAmpli = new List<double>() {1.0};//default value  
        public static double DisplayLoadAmpli = 1.0; //default value
        public static int DisplayDecimals = 1;

        public static double DisplayDyn = 0.005; //For the size of the masses considered in the dynamic computation
        #endregion Display
    }
}