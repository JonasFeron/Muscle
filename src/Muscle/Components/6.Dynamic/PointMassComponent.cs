using Grasshopper.Kernel;
using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;
using Muscle.View;
using Rhino.Geometry;
using System;
using static Muscle.Components.GHComponentsFolders;

namespace Muscle.Components.Dynamic
{
    public class PointMassComponent : GH_Component
    {
        #region Properties

        public override Guid ComponentGuid { get { return new Guid("f205aef9-149d-445e-b6c7-c49dda7f46f0"); } }

        #endregion Properties

        #region Constructors

        public PointMassComponent() :
                    base("Construct Point Mass", "Mass", "Construct a Point Mass by defining a mass and its point of application.", GHAssemblyName, Folder6_Dynamic)
        {
        }

        #endregion Constructors

        #region Methods

        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Point", "P", "Point or Node or Index of the node where the mass is applied.", GH_ParamAccess.item);
            pManager.HideParameter(0);
            pManager.AddNumberParameter("Mass", "m (kg)", "Mass in kg to apply on the node. The mass is duplicated in the X, Y, and Z directions since it is associated to acceleration of vibrations in all directions.", GH_ParamAccess.item);
        }



        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Point Mass", "m (kg)", "Mass applied on a node.", GH_ParamAccess.item);
        }

        protected override void SolveInstance(IGH_DataAccess DA)
        {
            GH_ObjectWrapper obj = new GH_ObjectWrapper(); // Point or Node or Index of the node where the mass is applied
            double mass = 0;

            if (!DA.GetData(0, ref obj)) { return; }
            if (!DA.GetData(1, ref mass)) { return; }


            if (mass < 0)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Mass must be a positive number in [kg]");
                return;
            }


            PointMass pointMass = null;

            #region retrieve point to create point load
            if (obj.Value is Node) // input is a node
            {
                Node node = obj.Value as Node;
                pointMass = new PointMass(node, mass);
            }
            else if (obj.Value is GH_Point) // input is a GH_Point
            {
                Point3d point = (obj.Value as GH_Point).Value;
                pointMass = new PointMass(point, mass);
            }
            else if (obj.Value is Point3d) // input is a Point3d
            {
                Point3d point = (Point3d)obj.Value;
                pointMass = new PointMass(point, mass);
            }
            else
            {
                // Try to convert to integer for node index
                GH_Integer gh_ind = new GH_Integer();
                if (gh_ind.CastFrom(obj.Value))
                {
                    int nodeIndex = gh_ind.Value;
                    pointMass = new PointMass(nodeIndex, mass);
                }
                else
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Input must be a Node, Point3d, or index");
                    return;
                }
            }
            #endregion retrieve point to create point load

            if (!pointMass.IsValid)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Invalid Point Mass");
                return;
            }
            DA.SetData(0, new GH_PointMass(pointMass));
        }

        #endregion Methods
    }
}