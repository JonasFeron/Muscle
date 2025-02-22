class State():
    def __init__(Cur):
        """
        The Current State of a Structure Object is defined by
        :param NodesCoord: The current nodes coordinates of the structure
        :param Loads: The total loads currently applied on the structure
        :param Tension: The internal tension forces currently existing in the structure
        :param Reactions: The reactions forces currently applied on the structure by the structure fixations
        """
        ##### State inputs #####
        # all methods of the state object will take a StructureObj as an argument which contains all data that do not vary in time, for instance
        NodesCount = 0
        ElementsCount = 0
        FixationsCount = 0
        DOFfreeCount = 0
        # as well as other data: area, young modulus, ...

        ##### Initialize the State properties #####
        Cur.NodesCoord = np.zeros((3*NodesCount,))
        Cur.Loads = np.zeros((3*NodesCount,))
        Cur.Tension = np.zeros((ElementsCount,))
        Cur.Reactions = np.zeros((FixationsCount,))

        Cur.ElementsA = np.zeros((ElementsCount,)) # Area [mm²] - the areas in the current state depend if each element is in tension or compression
        Cur.ElementsE = np.zeros((ElementsCount,)) # Young Modulus [MPa] - the young modulus in the current state depend if each element is in tension or compression

        Cur.ElementsL = np.zeros((ElementsCount,))  # Current Elements lengths
        Cur.ElementsLFree = np.zeros((ElementsCount,))  # Lengths of the elements when the elements are free of any tension, or in other words, when the structure is disassemble.
        Cur.ElementsCos = np.zeros((ElementsCount, 3))  # The cosinus directors of the elements
        Cur.A = np.zeros((3 * NodesCount, ElementsCount))  # The equilibrium matrix of the structure in the current state
        Cur.AFree = np.zeros((DOFfreeCount,ElementsCount))  # Equilibrium matrix of the free degrees of freedom only
        Cur.AFixed = np.zeros((FixationsCount,ElementsCount))  # Equilibrium matrix of the fixed degrees of freedom only. Allows to find reactions from tension forces. AFixed @ Tension = Reaction
        Cur.SVD = ResultsSVD()  # An empty results SVD object

        Cur.Residual = np.ones((3 * NodesCount,))  # the unbalanced loads = All external Loads - A @ Tension
        Cur.IsInEquilibrium = False  # the current state of the structure is in equilibrum if the unbalanced loads (Residual) are below a certain threshold (very small)
        Cur.Flex = np.zeros((ElementsCount,))  # the current flexbilities Lfree/EA of the elements depending on the sign of the force in the element
        Cur.Kmat = np.zeros((3 * NodesCount, 3 * NodesCount))  # global material stiffness matrix
        Cur.Kgeo = np.zeros((3 * NodesCount, 3 * NodesCount))  # global geometrical stiffness matrix
        Cur.DRState = DRState()