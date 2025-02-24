
namespace MuscleCore.FEModel
{
    public class FEM_Structure
    {
        public FEM_Nodes Nodes { get; set; }
        public FEM_Elements Elements { get; set; }
        public FEM_Actions Additional { get; set; } // Additional actions (Loads and Prestress) on the structure
        public FEM_Actions Applied { get; set; } // Already applied actions (Loads and Prestress) on the structure
        public FEM_NodesResults InitialNodesResults { get; set; } // Previous nodes results (from the already applied actions)
        public FEM_ElementsResults InitialElementsResults { get; set; } // Previous elements results (from the already applied actions)
        public FEM_Structure()
        {
            Nodes = new FEM_Nodes();
            Elements = new FEM_Elements();
            Additional = new FEM_Actions();
            Applied = new FEM_Actions();
            InitialNodesResults = new FEM_NodesResults();
            InitialElementsResults = new FEM_ElementsResults();
        }
        public FEM_Structure(FEM_Nodes nodes, FEM_Elements elements)
        {
            Nodes = nodes;
            Elements = elements;
            Additional = new FEM_Actions();
            Applied = new FEM_Actions();
            InitialNodesResults = new FEM_NodesResults();
            InitialElementsResults = new FEM_ElementsResults();
        }

        public FEM_Structure(FEM_Nodes nodes, FEM_Elements elements, FEM_Actions additional)
        {
            Nodes = nodes;
            Elements = elements;
            Additional = additional;
            Applied = new FEM_Actions();
            InitialNodesResults = new FEM_NodesResults();
            InitialElementsResults = new FEM_ElementsResults();
        }

        public FEM_Structure(FEM_Nodes nodes, FEM_Elements elements, FEM_Actions additional, FEM_Actions applied, FEM_NodesResults initialNodesResults, FEM_ElementsResults initialElementsResults)
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
