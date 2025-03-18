using MuscleCore.FEModel;
using Python.Runtime;

namespace MuscleCore.Converters
{
    public class PyNodesEncoder : IPyObjectEncoder
    {
        public bool CanEncode(Type type)
        {
            return type == typeof(CoreNodes);
        }

        public PyObject? TryEncode(object obj)
        {
            if (!CanEncode(obj.GetType()))
                return null;

            var nodes = (CoreNodes)obj;
            using (Py.GIL())
            {
                dynamic musclepy = Py.Import("MusclePy");

                return musclepy.PyNodes(
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
