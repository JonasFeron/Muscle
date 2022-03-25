using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace Muscles.Dynamics
{
    public class DynamicsComponent : GH_Component
    {
        public DynamicsComponent() : base("MyFirst", "MFC", "My first component", "Extra", "Simple")
        {
        }
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            throw new NotImplementedException();
        }

        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            throw new NotImplementedException();
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            throw new NotImplementedException();
        }

        public override Guid ComponentGuid
        {
            get { return new Guid("27be22c5-b58c-456d-9fa2-b8eb420de98d"); }
        }
    }
}
