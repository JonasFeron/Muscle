
namespace Muscle.FEModel
{
    public class FEM_StructureResults
    {
        public FEM_Actions Total { get; set; } // Total actions (Loads and Prestress) on the structure
        public FEM_NodesResults TotalNodes { get; set; } // Total nodes results (displacements, reactions, ... from the total actions)
        public FEM_ElementsResults TotalElements { get; set; } // Total elements results (tensions, elongations, ... from the total actions)
        public FEM_StructureResults()
        {
            Total = new FEM_Actions();
            TotalNodes = new FEM_NodesResults();
            TotalElements = new FEM_ElementsResults();
        }
    }
}
