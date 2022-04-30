using Grasshopper;
using Grasshopper.Kernel;
using System;
using System.Drawing;

namespace Muscle
{
    public class LogHelper : GH_AssemblyInfo
    {
        public override string Name => "Muscle";

        //Return a 24x24 pixel bitmap to represent this GHA library.
        public override Bitmap Icon => null;

        //Return a short string describing the purpose of this GHA library.
        public override string Description => "";

        public override Guid Id => new Guid("4C470200-9416-4DB5-A52C-16E772DC62FC");

        //Return a string identifying you or your company.
        public override string AuthorName => "";

        //Return a string representing your preferred contact details.
        public override string AuthorContact => "";
    }
}