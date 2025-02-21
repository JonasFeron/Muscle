
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
    }
}
