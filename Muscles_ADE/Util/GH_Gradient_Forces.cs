using System;
using System.Drawing;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Grasshopper.GUI.Gradient;

namespace Muscles_ADE.Util
{
    class GH_Gradient_Forces
    {
        #region Properties
        public GH_Gradient gradient;
        #endregion Properties

        #region Constructors
        public GH_Gradient_Forces()
        {
            gradient = new GH_Gradient();
            gradient.Linear = true; //linear interpolation of the colors
            gradient.AddGrip(-1, Color.Red); //compression
            gradient.AddGrip(0, Color.White); //0
            gradient.AddGrip(1, Color.Blue); //Tension
        }


        #endregion Constructors

    }
}
