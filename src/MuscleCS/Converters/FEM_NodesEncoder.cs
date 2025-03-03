using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class FEM_NodesEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(FEM_Nodes);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var nodes = (FEM_Nodes)obj;
            using (Py.GIL())
            {
                dynamic fem_nodes = Py.Import("MusclePy.femodel.fem_nodes");

                return fem_nodes.FEM_Nodes(
                        initial_coordinates: nodes.InitialCoordinates,
                        dof: nodes.DOF,
                        loads: nodes.Loads,
                        displacements: nodes.Displacements,
                        reactions: nodes.Reactions,   
                        resisting_forces: nodes.ResistingForces
                    );
            }
        }
    }
}
