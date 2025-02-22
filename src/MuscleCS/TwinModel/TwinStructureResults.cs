
namespace MuscleCore.TwinModel
{
    public class TwinStructureResults
    {
        public TwinActions Total { get; set; } // Total actions (Loads and Prestress) on the structure
        public TwinNodesResults TotalNodes { get; set; } // Total nodes results (displacements, reactions, ... from the total actions)
        public TwinElementsResults TotalElements { get; set; } // Total elements results (tensions, elongations, ... from the total actions)
        public TwinStructureResults()
        {
            Total = new TwinActions();
            TotalNodes = new TwinNodesResults();
            TotalElements = new TwinElementsResults();
        }
    }
}
