using System;
using System.Drawing;
using Grasshopper.Kernel;

namespace Muscle
{
    public class MusclesInfo : GH_AssemblyInfo
    {
        public override string Name
        {
            get
            {
                return "Muscles";
            }
        }
        public override Bitmap Icon
        {
            get
            {
                //Return a 24x24 pixel bitmap to represent this GHA library.
                return null;
            }
        }
        public override string Description
        {
            get
            {
                //Return a short string describing the purpose of this GHA library.
                return "";
            }
        }
        public override Guid Id
        {
            get
            {
                return new Guid("9c0e7385-99b5-4995-b45a-a77fc0a2b1df");
            }
        }

        public override string AuthorName
        {
            get
            {
                //Return a string identifying you or your company.
                return "";
            }
        }
        public override string AuthorContact
        {
            get
            {
                //Return a string representing your preferred contact details.
                return "";
            }
        }
    }
}
