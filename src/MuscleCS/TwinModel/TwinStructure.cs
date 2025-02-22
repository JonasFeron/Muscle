
namespace MuscleCore.TwinModel
{
    public class TwinStructure
    {
        public TwinNodes Nodes { get; set; }
        public TwinElements Elements { get; set; }
        public TwinActions Additional { get; set; } // Additional actions (Loads and Prestress) on the structure
        public TwinActions Applied { get; set; } // Already applied actions (Loads and Prestress) on the structure
        public TwinNodesResults InitialNodesResults { get; set; } // Previous nodes results (from the already applied actions)
        public TwinElementsResults InitialElementsResults { get; set; } // Previous elements results (from the already applied actions)
        public TwinStructure()
        {
            Nodes = new TwinNodes();
            Elements = new TwinElements();
            Additional = new TwinActions();
            Applied = new TwinActions();
            InitialNodesResults = new TwinNodesResults();
            InitialElementsResults = new TwinElementsResults();
        }
        public TwinStructure(TwinNodes nodes, TwinElements elements)
        {
            Nodes = nodes;
            Elements = elements;
            Additional = new TwinActions();
            Applied = new TwinActions();
            InitialNodesResults = new TwinNodesResults();
            InitialElementsResults = new TwinElementsResults();
        }

        public TwinStructure(TwinNodes nodes, TwinElements elements, TwinActions additional)
        {
            Nodes = nodes;
            Elements = elements;
            Additional = additional;
            Applied = new TwinActions();
            InitialNodesResults = new TwinNodesResults();
            InitialElementsResults = new TwinElementsResults();
        }

        public TwinStructure(TwinNodes nodes, TwinElements elements, TwinActions additional, TwinActions applied, TwinNodesResults initialNodesResults, TwinElementsResults initialElementsResults)
        {
            Nodes = nodes;
            Elements = elements;
            Additional = additional;
            Applied = applied;
            InitialNodesResults = initialNodesResults;
            InitialElementsResults = initialElementsResults;
        }
    }
}
