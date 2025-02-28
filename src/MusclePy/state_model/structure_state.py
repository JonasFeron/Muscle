from MusclePy.state_model.elements_state import Elements_State
from MusclePy.state_model.nodes_state import Nodes_State



class State():
    def __init__(self, nodes=None, elements=None, applied=None, initial_nodes_results=None, initial_elements_results=None):
        """
        The current State of a Structure Object is defined by
        :param NodesCoord: The current nodes coordinates of the structure
        :param Loads: The total loads currently applied on the structure
        :param Tension: The internal tension forces currently existing in the structure
        :param Reactions: The reactions forces currently applied on the structure by the structure fixations
        """
        # ##### State inputs #####
        # # all methods of the state object will take a StructureObj as an argument which contains all data that do not vary in time, for instance
        # NodesCount = 0
        # ElementsCount = 0
        # FixationsCount = 0
        # DOFfreeCount = 0
        # # as well as other data: area, young modulus, ...

        # ##### Initialize the State properties #####
        # self.NodesCoord = np.zeros((3*NodesCount,))
        # self.Loads = np.zeros((3*NodesCount,))
        # self.Tension = np.zeros((ElementsCount,))
        # self.Reactions = np.zeros((FixationsCount,))

        # self.ElementsA = np.zeros((ElementsCount,)) # Area [mm²] - the areas in the selfrent state depend if each element is in tension or compression
        # self.ElementsE = np.zeros((ElementsCount,)) # Young Modulus [MPa] - the young modulus in the selfrent state depend if each element is in tension or compression

        # self.ElementsL = np.zeros((ElementsCount,))  # selfrent Elements lengths
        # self.ElementsLFree = np.zeros((ElementsCount,))  # Lengths of the elements when the elements are free of any tension, or in other words, when the structure is disassemble.
        # self.ElementsCos = np.zeros((ElementsCount, 3))  # The cosinus directors of the elements
        # self.A = np.zeros((3 * NodesCount, ElementsCount))  # The equilibrium matrix of the structure in the selfrent state
        # self.AFree = np.zeros((DOFfreeCount,ElementsCount))  # Equilibrium matrix of the free degrees of freedom only
        # self.AFixed = np.zeros((FixationsCount,ElementsCount))  # Equilibrium matrix of the fixed degrees of freedom only. Allows to find reactions from tension forces. AFixed @ Tension = Reaction
        # self.SVD = ResultsSVD()  # An empty results SVD object

        # self.Residual = np.ones((3 * NodesCount,))  # the unbalanced loads = All external Loads - A @ Tension
        # self.IsInEquilibrium = False  # the selfrent state of the structure is in equilibrum if the unbalanced loads (Residual) are below a certain threshold (very small)
        # self.Flex = np.zeros((ElementsCount,))  # the selfrent flexbilities Lfree/EA of the elements depending on the sign of the force in the element
        # self.Kmat = np.zeros((3 * NodesCount, 3 * NodesCount))  # global material stiffness matrix
        # self.Kgeo = np.zeros((3 * NodesCount, 3 * NodesCount))  # global geometrical stiffness matrix
        # self.DRState = DRState()

        # def __init__(self)):
        # """Python equivalent of C# Twin_Structure class"""
        self.nodes = Nodes_State(nodes,applied,initial_nodes_results)  
        self.elements = Elements_State(elements,self.nodes,applied,initial_elements_results) 

        # # Additional actions (Loads and Prestress) on the structure
        # self.additional = Twin_Actions(additional) if additional is not None else Twin_Actions()

        # # Already applied actions (Loads and Prestress) on the structure  
        # self.applied = Twin_Actions(applied) if applied is not None else Twin_Actions() 

        # # Previous nodes results (from the already applied actions) 
        # self.initial_nodes_results = Twin_NodesResults(initial_nodes_results) if initial_nodes_results is not None else Twin_NodesResults()

        # # Previous elements results (from the already applied actions) 
        # self.initial_elements_results = Twin_ElementsResults(initial_elements_results) if initial_elements_results is not None else Twin_ElementsResults()



