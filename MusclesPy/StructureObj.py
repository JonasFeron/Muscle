import numpy as np
from data import SharedData

class ResultsSVD():

    def __init__(SVD,NodesCount = 0,ElementsCount = 0,FixationsCount = 0):
        DOFfreeCount = 3*NodesCount - FixationsCount

        SVD.S = np.zeros((DOFfreeCount,)) #eigen values of A_free
        SVD.r = 0  # number of non null eigen value. rank of A_free
        SVD.Sr = np.zeros((SVD.r,)) #non null eigen values of A_free

        SVD.s = ElementsCount - SVD.r #degree of static indeterminacy = nbr of self-stress modes
        SVD.Vr_row = np.zeros((SVD.r, ElementsCount)) # r row eigen vectors. Interpretation: Bar tensions in equilibrium with the Diag(S)* Loads of Ur OR Bar elongations compatible with Diag(1/S) * Extensional displacements of Ur
        SVD.Vs_row = np.zeros((SVD.s, ElementsCount)) # s row eigen vectors. Interpretation: Self-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
        SVD.SS = np.zeros((SVD.s, ElementsCount))  # s row eigen vectors. =Vs_row but rescaled to have the biggest force = -1 (compression) in each vector. Interpretation: rescaled Self-stress modes

        SVD.m = DOFfreeCount - SVD.r #degree of kinematic indeterminacy = nbr of mechanisms
        SVD.Ur_row = np.zeros((SVD.r, 3 * NodesCount)) #same as free but considering 0 reaction/displacement at the support.
        SVD.Ur_free_row = np.zeros((SVD.r, DOFfreeCount)) # r row eigenvectors. Interpretation: Loads which can be equilibrated in the current struct OR Extensional displacements
        SVD.Um_row = np.zeros((SVD.m, 3 * NodesCount)) #same as free but considering 0 reaction/displacement at the support.
        SVD.Um_free_row = np.zeros((SVD.m, DOFfreeCount)) # m row eigenvectors. Interpretation: Loads which can not be equilibrated in the current struct OR Inextensional displacements (sol of B@d = 0)

    def PopulateWith(SVD,S,r,Sr,s,Vr_row,Vs_row,SS,m,Ur_row,Ur_free_row,Um_row,Um_free_row):
        SVD.S = S
        SVD.r = r
        SVD.Sr = Sr

        SVD.s = s
        SVD.Vr_row = Vr_row
        SVD.Vs_row = Vs_row
        SVD.SS = SS

        SVD.m = m
        SVD.Ur_row = Ur_row
        SVD.Ur_free_row = Ur_free_row
        SVD.Um_row = Um_row
        SVD.Um_free_row = Um_free_row

class State():
    def __init__(Cur, Nodes_coord, Tension_applied, Loads_applied, Loads_to_apply):
        """
        The Current State of a Structure Object is defined by
        :param Nodes_coord: The current nodes coordinates of the structure
        :param Loads_applied:
        :param Tension_applied:
        :param Reactions_applied:
        :param Loads_to_apply:
        """

        ##### Structure informations #####

        cur.Nodes_coord = Nodes_coord.reshape((-1, 1))
        cur.Elements_EndNodes = S0.Elements_EndNodes
        cur.Elements_L0 = S0.Elements_L0
        cur.Elements_Cos0 = S0.Elements_Cos0
        cur.Elements_A = S0.Elements_A
        cur.Elements_E = S0.Elements_E
        cur.IsDOFfree = S0.IsDOFfree
        # Elements info
        cur.C = S0.C

        # S0.Loads_Already_Applied = np.zeros((S0.NodesCount, 3))
        cur.Loads_To_Apply = Loads_To_Apply.reshape((-1, 1))
        cur.AxialForces_Already_Applied = AxialForces_Already_Applied.reshape((-1, 1))

        # S0.Displacements_Already_Applied = np.zeros((S0.NodesCount,3))  # this is such that this.Nodes_coord = NodesCoord0 + this.Displacements_Already_Applied. If the structure is solved for the first time,Displacements_Already_Applied =0.
        # S0.Displacements_Results = np.zeros((S0.NodesCount, 3))  # results from Loads_To_Apply

        # S0.Reactions_Already_Applied = np.zeros((S0.FixationsCount,))
        # S0.Reactions_Results = np.zeros((S0.FixationsCount,))  # results from Loads_To_Apply
        return cur


class StructureObj():


    # region Constructors
    def __init__(S0, NodesCount = 0, ElementsCount = 0, FixationsCount = 0):
        """
        Initialize an empty structure
        """
        S0.NodesCount = NodesCount
        S0.ElementsCount = ElementsCount
        S0.FixationsCount = FixationsCount
        S0.DOFfreeCount = 3 * NodesCount - FixationsCount

        ##### Structure informations #####

        S0.Nodes_coord = np.zeros((3 * S0.NodesCount, 1))
        S0.Elements_EndNodes = np.zeros((S0.ElementsCount, 2), dtype=int)
        S0.Elements_A = np.zeros((S0.ElementsCount,1))
        S0.Elements_E = np.zeros((S0.ElementsCount,1))
        S0.IsDOFfree = np.zeros((3 * S0.NodesCount,), dtype=bool)

        #Elements info
        S0.C = np.zeros((S0.ElementsCount, S0.NodesCount), dtype=int) #matrice de connectivité C # (nbr lines, nbr nodes)
        S0.Elements_L0 = np.zeros((S0.ElementsCount,1)) # Lengths of the elements in the initial structure # (nbr lines,)
        S0.Elements_Cos0 = np.zeros((S0.ElementsCount, 3)) # Cos directors of the elements in the initial structure #(nbr lines,3)
        S0.F = np.eye(S0.ElementsCount, S0.ElementsCount) # Flexibility matrix containing L0/EA of each element in the diagonal

        S0.Elements_L = np.zeros((S0.ElementsCount,1))  # Lengths of the elements in the current structure. (Initial = Current at the first step of NL Solve)
        S0.Elements_Cos = np.zeros((S0.ElementsCount, 3)) # (nbr lines,3)

        ##### Assembly informations #####
        S0.A = np.zeros((3 * S0.NodesCount, S0.ElementsCount)) #Equilibrium matrix
        S0.A_free = np.zeros((S0.DOFfreeCount, S0.ElementsCount)) #Equilibrium matrix of the free dof only
        S0.A_fixed = np.zeros((S0.FixationsCount, S0.ElementsCount))  # Equilibrium matrix of the fixed dof only. Allows to find reactions from axial forces. A_fixed@t=r

        S0.SVD = ResultsSVD() #object containing all the results of the Singular Value Decomposition of the Equilibrium matrix

        # =!0 if E and A are non null
        S0.Km = np.zeros((3 * S0.NodesCount, 3 * S0.NodesCount))
        S0.Km_free = np.zeros((S0.DOFfreeCount, S0.DOFfreeCount))

        S0.K_constrained = np.zeros((3 * S0.NodesCount + S0.FixationsCount,
                                     3 * S0.NodesCount + S0.FixationsCount))  # required to solve the structure with imposed displacements of the supports

        # ##### Solve informations #####
        S0.n_steps = 1
        S0.Stages = np.ones((1,))

        S0.Loads_Already_Applied = np.zeros((3*S0.NodesCount,1))
        S0.Loads_To_Apply = np.zeros((3*S0.NodesCount,1))
        # S0.Loads_Applied = np.zeros((3*S0.NodesCount,))
        # S0.Loads_Total = np.zeros((S0.NodesCount, 3)) # Already_Applied + To_Apply

        S0.AxialForces_Already_Applied = np.zeros((S0.ElementsCount,1)) #considered in Geometric stiffness
        S0.AxialForces_Results = np.zeros((S0.ElementsCount,1)) #results from Loads_To_Apply
        # S0.AxialForces_Total = np.zeros((S0.ElementsCount,)) # Results + Already_Applied
        S0.Elongations_To_Apply = np.zeros((S0.ElementsCount,1))

        # S0.Displacements_Already_Applied = np.zeros((S0.NodesCount,3)) # this is such that this.Nodes_coord = NodesCoord0 + this.Displacements_Already_Applied. If the structure is solved for the first time,Displacements_Already_Applied =0.
        S0.Displacements_Results = np.zeros((3*S0.NodesCount,1)) #results from Loads_To_Apply
        # S0.Displacements_Total = np.zeros((S0.NodesCount, 3)) # Results + Already_Applied

        # S0.Reactions_Already_Applied = np.zeros((S0.FixationsCount,))
        S0.Reactions_Results = np.zeros((S0.FixationsCount,1)) #results from Loads_To_Apply
        # S0.Reactions_Total = np.zeros((S0.FixationsCount,)) # Results + Already_Applied

        # S0.AxialForces_To_Apply
        #
        # ##### Calculation Results #####

    def NewStructureObj(S0, NewNodesCoord, AxialForces_Already_Applied, Loads_To_Apply):
        """
        Initialize a new current structure object based on a initial structure.
        """
        cur = StructureObj(S0.NodesCount, S0.ElementsCount,
                           S0.FixationsCount)  # Each Current structure Obj is considered as an Initial Structure Object. The only difference is that their nodes coordinates have changed compared to Initial.

        ##### Structure informations #####

        cur.Nodes_coord = NewNodesCoord.reshape((-1, 1))
        cur.Elements_EndNodes = S0.Elements_EndNodes
        cur.Elements_L0 = S0.Elements_L0
        cur.Elements_Cos0 = S0.Elements_Cos0
        cur.Elements_A = S0.Elements_A
        cur.Elements_E = S0.Elements_E
        cur.IsDOFfree = S0.IsDOFfree
        # Elements info
        cur.C = S0.C

        # S0.Loads_Already_Applied = np.zeros((S0.NodesCount, 3))
        cur.Loads_To_Apply = Loads_To_Apply.reshape((-1,1))
        cur.AxialForces_Already_Applied = AxialForces_Already_Applied.reshape((-1,1))

        # S0.Displacements_Already_Applied = np.zeros((S0.NodesCount,3))  # this is such that this.Nodes_coord = NodesCoord0 + this.Displacements_Already_Applied. If the structure is solved for the first time,Displacements_Already_Applied =0.
        # S0.Displacements_Results = np.zeros((S0.NodesCount, 3))  # results from Loads_To_Apply

        # S0.Reactions_Already_Applied = np.zeros((S0.FixationsCount,))
        # S0.Reactions_Results = np.zeros((S0.FixationsCount,))  # results from Loads_To_Apply
        return cur
    # endregion

    # region Public Methods : Main
    def Main_Assemble(S0,Data):
        S0.PopulateWith(Data)
        S0.Core_Assemble()
        S0.SVD = S0.SVD_Equilibrium_Matrix(S0.A_free)

    def test_Main_Assemble(S0, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A=None, Elements_E=None):
        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E)
        S0.Core_Assemble()
        S0.SVD = S0.SVD_Equilibrium_Matrix(S0.A_free)

    def Main_LinearSolve_Displ_Method(S0,Data):
        S0.PopulateWith(Data)
        S0.Core_LinearSolve_Displ_Method()

    def test_Main_LinearSolve_Displ_Method(S0, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E, AxialForces_Already_Applied, Loads_To_Apply):
        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E,AxialForces_Already_Applied,Loads_To_Apply)
        S0.Core_LinearSolve_Displ_Method()

    def Main_NonLinearSolve_Displ_Method(S0,Data):
        S0.PopulateWith(Data)
        S0.Core_NonLinearSolve_Displ_Method()

    def test_Main_NonLinearSolve_Displ_Method(S0, n_steps, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E, AxialForces_Already_Applied, Loads_To_Apply):
        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E,AxialForces_Already_Applied,Loads_To_Apply,n_steps)
        S0.Core_NonLinearSolve_Displ_Method()

    def test_Main_LinearSolve_Force_Method(S0, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E, AxialForces_Already_Applied, Loads_To_Apply,Loads_Already_Applied,Elongations_To_Apply):
        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E,AxialForces_Already_Applied,Loads_To_Apply,1,Loads_Already_Applied,Elongations_To_Apply)
        S0.Core_LinearSolve_Force_Method()

    def test_Main_NonLinearSolve_Force_Method(S0,n_steps,NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E, AxialForces_Already_Applied, Loads_To_Apply,Loads_Already_Applied,Elongations_To_Apply):
        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E,AxialForces_Already_Applied,Loads_To_Apply,n_steps,Loads_Already_Applied,Elongations_To_Apply)
        S0.Core_NonLinearSolve_Force_Method()
    # endregion

    # region Private Methods : Retrieve the inputs
    def PopulateWith(S0,Data):
        if isinstance(Data,SharedData):
            S0.RegisterData(Data.NodesCoord,Data.Elements_ExtremitiesIndex,Data.IsDOFfree,Data.Elements_A,Data.Elements_E,Data.AxialForces_Already_Applied,Data.Loads_To_Apply,Data.n_steps)


    def RegisterData(S0, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A=np.zeros((0,)), Elements_E=np.zeros((0,)),
                     AxialForces_Already_Applied=np.zeros((0,)), Loads_To_Apply=np.zeros((0,)),n_steps=1,Loads_Already_Applied=np.zeros((0,)),Elongations_To_Apply=np.zeros((0,))):

        if isinstance(NodesCoord, np.ndarray):
            S0.NodesCount = NodesCoord.reshape(-1, 3).shape[0]
            S0.Nodes_coord = NodesCoord.reshape(-1, 1)
        else:
            S0.Nodes_coord = None
            S0.NodesCount = -1

        if isinstance(Elements_ExtremitiesIndex, np.ndarray):
            S0.Elements_EndNodes = Elements_ExtremitiesIndex.reshape(-1, 2).astype(int)
            S0.ElementsCount = S0.Elements_EndNodes.shape[0]
        else:
            S0.Elements_EndNodes = None
            S0.ElementsCount = -1

        if isinstance(IsDOFfree, np.ndarray):
            S0.IsDOFfree = IsDOFfree.reshape((-1,)).astype(bool)
            S0.DOFfreeCount = np.sum(np.ones(3 * S0.NodesCount, dtype=int)[S0.IsDOFfree])
            S0.FixationsCount = 3 * S0.NodesCount - S0.DOFfreeCount
        else:
            S0.IsDOFfree = None
            S0.FixationsCount = -1
            S0.DOFfreeCount = -1

        if isinstance(Elements_A, np.ndarray) and Elements_A.size == S0.ElementsCount:
            S0.Elements_A = Elements_A.reshape((-1,1))
        else:
            S0.Elements_A = np.zeros((S0.ElementsCount,1))

        if isinstance(Elements_E, np.ndarray) and Elements_E.size == S0.ElementsCount:
            S0.Elements_E = Elements_E.reshape((-1,1))
        else:
            S0.Elements_E = np.zeros((S0.ElementsCount,1))

        if isinstance(AxialForces_Already_Applied, np.ndarray) and AxialForces_Already_Applied.size == S0.ElementsCount:
            S0.AxialForces_Already_Applied = AxialForces_Already_Applied.reshape((-1,1))
        else:
            S0.AxialForces_Already_Applied = np.zeros((S0.ElementsCount,1))

        if isinstance(Loads_To_Apply, np.ndarray) and Loads_To_Apply.size == 3 * S0.NodesCount:
            S0.Loads_To_Apply = Loads_To_Apply.reshape(-1, 1)
        else:
            S0.Loads_To_Apply = np.zeros((3*S0.NodesCount, 1))

        if n_steps >=1:
            S0.n_steps=n_steps
        else:
            S0.n_steps=1

        if isinstance(Loads_Already_Applied, np.ndarray) and Loads_Already_Applied.size == 3 * S0.NodesCount:
            S0.Loads_Already_Applied = Loads_Already_Applied.reshape(-1, 1)
        else:
            S0.Loads_Already_Applied = np.zeros((3*S0.NodesCount, 1))

        if isinstance(Elongations_To_Apply, np.ndarray) and Elongations_To_Apply.size == S0.ElementsCount:
            S0.Elongations_To_Apply = Elongations_To_Apply.reshape(-1, 1)
        else:
            S0.Elongations_To_Apply = np.zeros((S0.ElementsCount, 1))
    # endregion

    # region Private Methods : Assemble a structure

    def Core_Assemble(S0):
        """
        Assemble the equilibrim Matrix and the material stiffness matrix. N.B. Do not perfom the SVD -> do it separately
        :return:
        """
        S0.C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.Elements_EndNodes)
        (S0.Elements_L,S0.Elements_Cos) = S0.Compute_Elements_Geometry(S0.Nodes_coord, S0.C)
        (S0.A, S0.A_free, S0.A_fixed) = S0.Compute_Equilibrium_Matrix(S0.Elements_Cos,S0.C,S0.IsDOFfree)
        # if S0.Elements_A.sum()!=0 and S0.Elements_E.sum()!=0:
        #     S0.Km = S0.Compute_StiffnessMat_Matrix(S0.A, S0.Elements_L, S0.Elements_A, S0.Elements_E)
        #     S0.Km_free = S0.Compute_StiffnessMat_Matrix(S0.A_free, S0.Elements_L, S0.Elements_A, S0.Elements_E)

    def Connectivity_Matrix(S0, NodesCount, ElementsCount, Elements_EndNodes):
        """
        :return: créée la matrice de connectivité C de taille (nbr lines, nbr nodes)
        """

        #Calculation
        C = np.zeros((ElementsCount, NodesCount), dtype=int)  # matrice de connectivité C
        for line_ind, line_extremities in enumerate(Elements_EndNodes):
            n0 = line_extremities[0]
            n1 = line_extremities[1]
            C[line_ind, n0] = 1
            C[line_ind, n1] = -1

        # 3)Output
        return -C  # lets store the results. - signe because it makes more sense to do n1-n0 (than n0-n1).
        # print(C)

    def Compute_Elements_Geometry(S0,NodesCoord,C):
        """
        Calculates the Lines properties (Lengths, CosDir) based on the given Nodes_coord and Connectivity Matrix C, and store it in S0
        """
        assert C.shape==(S0.ElementsCount,S0.NodesCount),"check that shape of connectivity matrix C = (nbr lines, nbr nodes)"

        # get the current X, Y or Z coordinates of all nodes
        Coord_n_3 = NodesCoord.reshape((-1,3))
        X = Coord_n_3[:, 0]  # (nbr nodes,)
        Y = Coord_n_3[:, 1]
        Z = Coord_n_3[:, 2]

        # calculate the différence of coordinates between both extremities of each line
        D_X = C @ X  # gives X1-X0 for each line
        D_Y = C @ Y  # (nbr lines,) = (nbr lines, nbr nodes) @ (nbr nodes,)
        D_Z = C @ Z

        # calculate the initial length of each line
        Elements_L = np.sqrt(D_X ** 2 + D_Y ** 2 + D_Z ** 2)  # (nbr lines,)
        Diag_L_inv = np.diag(1 / Elements_L)  # (nbr lines, nbr lines) where only the diagonal is non nul

        # calculate the initial cos directors of each line
        Cos_X = Diag_L_inv @ D_X  # (nbr lines,)  = (nbr lines, nbr lines) @ (nbr lines,)
        Cos_Y = Diag_L_inv @ D_Y
        Cos_Z = Diag_L_inv @ D_Z

        Elements_Cos = np.hstack((Cos_X.reshape((-1,1)),Cos_Y.reshape((-1,1)),Cos_Z.reshape((-1,1))))

        return (Elements_L,Elements_Cos)


    def Compute_Equilibrium_Matrix(S0,Elements_Cos,C,IsDOFfree):
        """
        :return: Calculate the equilibrium matrix based on the current cos director
        """

        (b,n) = C.shape #(nbr lines, nbr nodes)
        C_t = C.transpose()

        Cos_X = Elements_Cos[:,0]
        Cos_Y = Elements_Cos[:,1]
        Cos_Z = Elements_Cos[:,2]

        # 2) calculate equilibrium matrix
        # for each node (corresponding to one row), if the line (corresponding to a column) is connected to the node, then the entry of A contains the cos director, else 0.
        Ax = C_t @ np.diag(Cos_X)  # (nbr nodes, nbr lines)  =  (nbr nodes, nbr lines) @ (nbr lines, nbr lines)
        Ay = C_t @ np.diag(Cos_Y)
        Az = C_t @ np.diag(Cos_Z)

        A = np.zeros((3 * n, b)) # (3*nbr nodes, nbr lines)

        # the dof are sorted like this [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        for i in range(n):
            A[3 * i, :] = Ax[i, :]
            A[3 * i + 1, :] = Ay[i, :]
            A[3 * i + 2, :] = Az[i, :]

        A_free = A[IsDOFfree]  # (nbr free dof, nbr lines)
        A_fixed = A[~IsDOFfree] # (nbr fixed dof, nbr lines)

        return (A,A_free,A_fixed)


    def SVD_Equilibrium_Matrix(S0, A_free):
        """
        Singular Value Decomposition
        :param A: la matrice d'équilibre de taille DOFfreeCount x ElementsCount
        :return: modifie la configuration pour stocker les données relatives à la SVD
        """
        # 1) retrieve data
        ElementsCount = S0.ElementsCount
        NodesCount = S0.NodesCount
        DOFfreeCount = S0.DOFfreeCount
        IsDOFfree = S0.IsDOFfree

        assert A_free.shape == (DOFfreeCount,ElementsCount), "check that shape of Equilibrium matrix Afree = (nbr free dof, nbr lines)"
        assert np.abs(A_free).sum() != 0, "check that Equilibrium Matrix A_free has been computed"

        # 2) calculate the eigenvalues and vectors
        U_free_col, S, V_row = np.linalg.svd(A_free)  # S contains the eigen values of A_free in decreasing order. U_col is a matrix (nbr free DOF,nbr free DOF) containing the column eigen vectors. V_row is a matrix (nbr lines,nbr lines) containing the row eigen vectors.

        Lambda_1 = S.max()
        Tol = Lambda_1 * 10 ** -3  # Tol is the limit below which an eigen value is considered as null.
        Sr = S[S >= Tol]  # non null eigen values
        r = Sr.size  #number of non null eigen value. rank of A_free
        m = DOFfreeCount - r  #degree of kinematic indeterminacy = nbr of mechanisms
        s = ElementsCount - r  #degree of static indeterminacy = nbr of self-stress modes

        # 3a) Interprete the eigenVectors in the elements space
        Vr_row = V_row[:r,:]  # r row eigen vectors (,nbr lines). Interpretation: Bar tensions in equilibrium with the Diag(S)* Loads of Ur OR Bar elongations compatible with Diag(1/S) * Extensional displacements of Ur
        Vs_row = np.zeros((s, ElementsCount)) # s row eigen vectors. Interpretation: Self-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
        SS = np.zeros((s, ElementsCount)) # s row eigen vectors. =Vs_row but rescaled to have the biggest force = -1 (compression) in each vector. Interpretation: rescaled Self-stress modes

        if s != 0:
            Vs_row = V_row[-s:,:]  # s Vecteurs (lignes) propres (associés aux VaP nulles) de longueur ElementsCount. Interprétations : Self-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
            bool = -Vs_row.min(axis=1) > Vs_row.max(axis=1)  # true if |compression max| > tension max
            max = np.where(bool, Vs_row.min(axis=1), Vs_row.max(axis=1))
            SS = (Vs_row.transpose() / -max).transpose()  # self-stress modes Matrix. we made sure the max value is always equal to 1 in compression whatever the modes

        # NB : Vr_t est orthogonal à Vs_t.  check : print(Vr_row.transpose()@Vs_row) return matrix zeros

        # 3b) Interprete the eigenVectors in the nodes space

        Ur_free_col = U_free_col[:,:r]  # r col eigenvectors (nbr free DOF,). Interpretation: Loads which can be equilibrated in the current struct OR Extensional displacements
        Ur_free_row = Ur_free_col.transpose()
        Ur_row = np.zeros((r, 3 * NodesCount)) # r row eigenvectors (,3 nbr nodes).
        Ur_row[:, IsDOFfree] = Ur_free_row

        Um_free_col = np.zeros((DOFfreeCount, m))
        Um_free_row = np.zeros((m, DOFfreeCount))
        Um_row = np.zeros((m, 3 * NodesCount))
        if m != 0:
            Um_free_col = U_free_col[:,r:] # m col eigenvectors (nbr free DOF,). Interpretation: Loads which can not be equilibrated in the current struct OR Inextensional displacements (sol of B@d = 0)
            Um_free_row = Um_free_col.transpose() # m row eigenvectors (,nbr free DOF)
            Um_row[:, IsDOFfree] = Um_free_row # m row eigenvectors (,3 nbr nodes)

        # NB : Ur est orthogonal à Um.  check : print(Ur.transpose()@Um) return matrix zeros

        # 4) Send Results
        SVD = ResultsSVD()
        SVD.PopulateWith(S,r,Sr,s,Vr_row,Vs_row,SS,m,Ur_row,Ur_free_row,Um_row,Um_free_row)
        return SVD

    def Compute_StiffnessMat_Matrix(S0,A,Elements_L,Elements_A,Elements_E):

        Diag_A = np.diag(Elements_A.reshape((-1,))) #(nbr lines, nbr lines)
        Diag_E = np.diag(Elements_E.reshape((-1,))) #(nbr lines, nbr lines)
        Diag_L_inv = np.diag(1 / Elements_L) #(nbr lines, nbr lines) #current length ! (not initial)

        Diag_EAsL = Diag_A @ Diag_E @ Diag_L_inv #(nbr lines, nbr lines)

        A = A  # (3*nbr nodes, nbr lines) Or if input A=A_free (nbr free dof, nbr lines)
        B = A.transpose() # (nbr lines, 3*nbr nodes)  Or if input A=A_free (nbr lines, nbr free dof)
        Km = A @ Diag_EAsL @ B # (3*nbr nodes, 3*nbr nodes) OR (nbr free dof, nbr free dof)

        return Km

    # endregion

    # region Private Methods : Linear Solver based on displacement methods

    def Core_LinearSolve_Displ_Method(S0):

        S0.C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.Elements_EndNodes)
        (S0.Elements_L0,S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.Nodes_coord, S0.C)

        perturb = 1e-6  # [m], à appliquer si matrice singulière uniquement

        d = np.zeros((3*S0.NodesCount,1))
        AxialForces = np.zeros((S0.ElementsCount,1))
        Reactions = np.zeros((S0.FixationsCount,1))

        try:
            (d, AxialForces, Reactions) = S0.LinearSolve_Displ_Method(S0.Nodes_coord, S0.AxialForces_Already_Applied, S0.Loads_To_Apply)

        except np.linalg.linalg.LinAlgError:
            # print("la matrice est singulière")
            NodesCoord_perturbed = S0.Perturbation(S0.Nodes_coord, S0.IsDOFfree, perturb)
            (d, AxialForces, Reactions) = S0.LinearSolve_Displ_Method(NodesCoord_perturbed, S0.AxialForces_Already_Applied,S0.Loads_To_Apply)
        finally:
            S0.Displacements_Results = d
            S0.AxialForces_Results = AxialForces
            S0.Reactions_Results = Reactions

    def LinearSolve_Displ_Method(cur, NodesCoord, AxialForces_Already_Applied, Loads_To_Apply):

        #1) Input
        n = cur.NodesCount
        c = cur.FixationsCount

        Elements_L0 = cur.Elements_L0 #  = S0.Elements_L0 : Initial Lengths
        Elements_A = cur.Elements_A
        Elements_E = cur.Elements_E
        C = cur.C

        Loads = Loads_To_Apply.reshape((-1, 1))
        d_Imposed = np.zeros((c, 1))
        To_Apply = np.vstack((Loads, d_Imposed))

        #2) Compute stiffness matrices. NB: computed with current Length and current Cos !
        (cur.Elements_L, cur.Elements_Cos) = cur.Compute_Elements_Geometry(NodesCoord, C)
        (List_km_loc, List_kg_loc) = cur.Compute_StiffnessMatGeo_LocalMatrices(cur.Elements_L, cur.Elements_Cos, Elements_A, Elements_E, AxialForces_Already_Applied)
        cur.K_constrained = cur.Compute_StiffnessMatGeo_Matrix(List_km_loc, List_kg_loc) # (3n+c,3n+c)

        #3) Solve Linear System  # NB: this might throw the exception np.linalg.linalg.LinAlgError that we need to catch somewhere
        d_and_Reactions = np.linalg.solve(cur.K_constrained, To_Apply)  # voir equation 2.7 page 32 du mémoire J.Feron
        #N.B. K*1000 helps when working with length in mm, otherwise we have N/mm which is really smalled. but it works when K is in N/m

        #4) Post-Process
        d = d_and_Reactions[:3 * n].reshape((-1,1))
        Reactions = - d_and_Reactions[3 * n:].reshape((-1,1))
        AxialForces = cur.Post_Process_Displ_Method(d, List_km_loc, List_kg_loc, cur.Elements_Cos)
        return (d, AxialForces, Reactions)

    def Compute_StiffnessMatGeo_LocalMatrices(cur, Elements_L, Elements_Cos, Elements_A, Elements_E,AxialForces_Already_Applied):
        """
            This is the old way of computing the local material and geometric stiffness matrices. It relies on the current nodes coordinates and the already applied axial forces.
            :return:    Liste (Bx1) local material stiffness matrices
                        Liste (Bx1) local geometric stiffness matrices
        """
        b = Elements_A.size
        A = Elements_A
        E = Elements_E
        L = Elements_L # this is the length in the current structure !


        t0 = AxialForces_Already_Applied

        List_km_loc = []
        List_kg_loc = []

        for i in np.arange(b):
            cx = Elements_Cos[i, 0] # this is the cos in the current stage
            cy = Elements_Cos[i, 1]
            cz = Elements_Cos[i, 2]
            cos = np.array([[-cx, -cy, -cz, cx, cy, cz]])
            R = np.dot(cos.transpose(), cos)  # local compatibility * local equilibrium
            km = E[i] * A[i] / L[i] * R  # material stiffness matrix

            kg = t0[i] / L[i] * np.array([[1, 0, 0, -1, 0, 0],
                                          [0, 1, 0, 0, -1, 0],
                                          [0, 0, 1, 0, 0, -1],
                                          [-1, 0, 0, 1, 0, 0],
                                          [0, -1, 0, 0, 1, 0],
                                          [0, 0, -1, 0, 0, 1]])  # geometric stiffness matrix

            List_km_loc.append(km)
            List_kg_loc.append(kg)

        return (List_km_loc, List_kg_loc)

    def Compute_StiffnessMatGeo_Matrix(cur, List_km_loc, List_kg_loc):
        """
            Objectif: Calcul la matrice de raideur global K de la structure dans la configuration déformée donnée
            :param struct: un objet structure composé d'éléments, de noeuds et d'appuis
            :param List_local_stiffness_matrices: une liste (Bx1) de matrices de raideur locales des éléments dans une configuration déformée donnée

            :return: K: la matrice de rigidité global de la structrue
            """
        n = cur.NodesCount
        b = cur.ElementsCount
        c = cur.FixationsCount
        IsDOFfree = cur.IsDOFfree
        Elements_ExtremitiesIndex=cur.Elements_EndNodes

        Km = np.zeros((3*n, 3*n))
        Kg = np.zeros((3*n, 3*n))

        #assembly of local matrices into a global one
        for i in np.arange(b):
            n0 = Elements_ExtremitiesIndex[i, 0]
            n1 = Elements_ExtremitiesIndex[i, 1]
            km = List_km_loc[i]
            kg = List_kg_loc[i]

            index = np.array([3 * n0, 3 * n0 + 1, 3 * n0 + 2, 3 * n1, 3 * n1 + 1, 3 * n1 + 2]) #global index
            for j in np.arange(6): #local index
                for j2 in np.arange(6):
                    Km[index[int(j)], index[int(j2)]] += km[int(j), int(j2)]
                    Kg[index[int(j)], index[int(j2)]] += kg[int(j), int(j2)]

        # Considerations of the fixations
        IndexDOFfixed = np.arange(3*n)[~IsDOFfree] #(nbr fixations,)

        constrains = np.zeros((c, 3*n))
        for ind_c, ind_dof in enumerate(IndexDOFfixed):
            constrains[ind_c,ind_dof]=1

        K_constrained = np.zeros((3 * n + c, 3 * n + c))
        K_constrained[:3*n,:3*n] = Km+Kg
        K_constrained[3*n:, :3*n] = constrains
        K_constrained[:3*n, 3*n:] = constrains.transpose()

        return K_constrained

    def Post_Process_Displ_Method(cur, d, List_km_loc, List_kg_loc, Elements_Cos):
        Elements_ExtremitiesIndex = cur.Elements_EndNodes
        b = cur.ElementsCount
        AxialForces = np.zeros((b,1))
        for i in np.arange(b):
            n0 = Elements_ExtremitiesIndex[i, 0]
            n1 = Elements_ExtremitiesIndex[i, 1]
            index = np.array([3*n0, 3*n0+1, 3*n0+2, 3*n1, 3*n1+1, 3*n1+2])
            d_loc = d[index] #(6,)  displacements at the extremities of the bars

            k_loc = List_km_loc[i] + List_kg_loc[i] #local stiffness matrix

            f_loc = k_loc @ d_loc #(6,) forces in the global coordinates

            cx = Elements_Cos[i, 0] #this is the cos in the current structure
            cy = Elements_Cos[i, 1]
            cz = Elements_Cos[i, 2]

            AxialForces[i] = -(f_loc[0] * cx + f_loc[1] * cy + f_loc[2] * cz) #forces in the local coordinates of the bar
            #AxialForces[i] = (f_loc[3] * cx + f_loc[4] * cy + f_loc[5] * cz) #equivalent
        return AxialForces

    def Perturbation(S0,NodesCoord,IsDOFfree,perturb):
        """
        Apply a perturbation on all nodes free in Z
        :return: NodesCoord_perturbed: vecteur (Nx3) des coordonnées des noeuds avec perturbation
        """
        NodesCoord_perturbed = NodesCoord.copy().reshape((-1,3))
        IsZfree = IsDOFfree.reshape((-1,3))[:,2]
        NodesCoord_perturbed[IsZfree,2] -= perturb
        return NodesCoord_perturbed.reshape((-1,1))

    # endregion

    # region Private Methods : Non Linear Solver based on displacement methods
    def Core_NonLinearSolve_Displ_Method(S0):

        S0.C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.Elements_EndNodes)
        (S0.Elements_L0,S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.Nodes_coord, S0.C)

        (Stages,StagesLoad,StagesDispl,StagesN,StagesR) = S0.NonLinearSolve_Displ_Method(S0.n_steps, S0.Nodes_coord, S0.AxialForces_Already_Applied, S0.Loads_To_Apply)
        S0.Stages = Stages
        S0.Loads_Applied = StagesLoad
        S0.Displacements_Results = StagesDispl
        S0.AxialForces_Results = StagesN - S0.AxialForces_Already_Applied #NB return only the additionnal tension coming from the loads to Apply; remove the tensions that were already present before
        S0.Reactions_Results = StagesR

    def NonLinearSolve_Displ_Method(S0,n_steps,NodesCoord0,AxialForces_Already_Applied, Loads_To_Apply):
        """
        Non linear solve of the structure. Input:
            NodesCoord0: Initial Nodes coordinates (Nx3)
            AxialForces_Already_Applied: Initial AxialForces in equilibrium in the structure (Bx1)
            Loads_To_Apply: Loads to apply on the nodes (Nx3)
        """
        AxialForcesInit = AxialForces_Already_Applied.reshape(-1,1)

        perturb = 1e-6  # [mm], to apply if singular matrix

        l0 = 1 / n_steps  # incremental length
        Max_n_steps = n_steps * 5 #max number of steps

        k = 0  # current step
        Stage = 0.0  # Initial Stage = 0. Final Stage = 1.

        p = Loads_To_Apply.reshape((-1,1)) #Load applied at each linear step. All the load is applied at each step
        v = np.zeros((3*S0.NodesCount,1))  #Displacement at each linear step. solution of K_k @ v = p where K_k is the stiffness matrix at the current step k
        N = np.zeros((S0.ElementsCount,1)) #AxialForce at each linear step
        R = np.zeros((S0.FixationsCount,1)) #Reaction at each linear step

        IncrStage = 0 #advance in the stage
        IncrLoad = np.zeros((3*S0.NodesCount,1)) #Incr of Load at this step. IncrLoad = Loads_To_Apply * IncrStage
        IncrDispl = np.zeros((3*S0.NodesCount,1))  #Incr of Displacement at this step. IncrDispl = v * IncrStage
        IncrN = np.zeros((S0.ElementsCount,1)) #Incr of AxialForce at this step. IncrN = N * IncrStage
        IncrR = np.zeros((S0.FixationsCount,1)) #Incr of Reaction at this step. IncrR = R * IncrStage

        # Stage 0
        Stages = np.array([Stage]) #succesion of stages
        StagesLoad = IncrLoad.copy() #list of applied load at all stages.
        StagesDispl = IncrDispl.copy() #list of Displacement at all stages.
        StagesN = AxialForcesInit.copy() #list of AxialForces at all stages.
        StagesR = IncrR.copy() #list of Reactions at all stages.

        while (Stage < 1 and k < Max_n_steps):

            # A new initial structure is considered at each step. A Linear Solve method is applied on it.
            CurDispl = StagesDispl[:,k].reshape((-1,1))
            CurNodesCoord = NodesCoord0 + CurDispl
            CurAxialForces = StagesN[:,k].reshape((-1,1))
            cur = S0.NewStructureObj(CurNodesCoord, CurAxialForces, p)

            try:
                (v, N, R) = cur.LinearSolve_Displ_Method(cur.Nodes_coord, cur.AxialForces_Already_Applied, cur.Loads_To_Apply)
            except np.linalg.LinAlgError:
                # print("la matrice est singulière")
                NodesCoord_perturbed = cur.Perturbation(cur.Nodes_coord, cur.IsDOFfree, perturb)
                (v, N, R) = cur.LinearSolve_Displ_Method(NodesCoord_perturbed,cur.AxialForces_Already_Applied,cur.Loads_To_Apply)
            finally:
                cur.Displacements_Results = v #Linear results
                cur.AxialForces_Results = N
                cur.Reactions_Results = R

                if k==0: # Initial Structure = current at first step
                    S0.Elements_L = cur.Elements_L
                    S0.Elements_Cos = cur.Elements_Cos
                    S0.K_constrained = cur.K_constrained

                if l0 == 1:  # if incremental length = 1
                    IncrStage = 1  #final stage is obtained in one step. NonLinear Method = Linear Method

                else:  # use arclength constrain
                    norm = (v.transpose() @ v)[0,0] #scalar product
                    f = np.sqrt(1 + norm) #scalar
                    IncrStage = (l0 / f) * np.sign(np.dot(p.transpose(), v))[0,0]  # it can be negative

                if Stage + IncrStage > 1:  # Ensure to stop exactly on Final Stage = 1.
                    IncrStage = 1 - Stage

                # Move to next step
                Stage = Stage + IncrStage
                IncrLoad = p * IncrStage
                IncrDispl = v * IncrStage
                IncrN = N * IncrStage
                IncrR = R * IncrStage

                #store the results of this stage
                Stages = np.hstack((Stages,Stage))
                StagesLoad= np.hstack((StagesLoad,StagesLoad[:,k].reshape((-1,1)) + IncrLoad))
                StagesDispl= np.hstack((StagesDispl,StagesDispl[:,k].reshape((-1,1)) + IncrDispl))
                StagesN = np.hstack((StagesN,StagesN[:,k].reshape((-1,1)) + IncrN))
                StagesR= np.hstack((StagesR,StagesR[:,k].reshape((-1,1)) + IncrR))

                k = k + 1

        if k == Max_n_steps:
            # print('nbr iterations du solveur non linéaire : {}/{}  progression Stage: {} %'.format(k, Max_n_steps,np.around(Stage * 100,decimals=2)))
            return (np.array([[]]),np.array([[]]),np.array([[]]),np.array([[]]),np.array([[]]))
        else:
            # print('nbr iterations du solveur non linéaire :', k)
            return (Stages,StagesLoad,StagesDispl,StagesN,StagesR)

    def NonLinearSolve_Displ_Method_NewtonRaphson(S0,n_steps,NodesCoord0,AxialForces_Already_Applied, Loads_To_Apply):
        """
        Non linear solve of the structure. Input:
            NodesCoord0: Initial Nodes coordinates (Nx3)
            AxialForces_Already_Applied: Initial AxialForces in equilibrium in the structure (Bx1)
            Loads_To_Apply: Loads to apply on the nodes (Nx3)
        """
        AxialForcesInit = AxialForces_Already_Applied.reshape(-1,1)

        perturb = 1e-6  # [mm], to apply if singular matrix

        l0 = 1 / n_steps  # incremental length
        Max_n_steps = n_steps * 5 #max number of steps

        k = 0  # current step
        Stage = 0.0  # Initial Stage = 0. Final Stage = 1.

        p = Loads_To_Apply.reshape((-1,1)) #Load applied at each linear step. All the load is applied at each step
        v = np.zeros((3*S0.NodesCount,1))  #Displacement at each linear step. solution of K_k @ v = p where K_k is the stiffness matrix at the current step k
        N = np.zeros((S0.ElementsCount,1)) #AxialForce at each linear step
        R = np.zeros((S0.FixationsCount,1)) #Reaction at each linear step

        IncrStage = 0 #advance in the stage
        IncrLoad = np.zeros((3*S0.NodesCount,1)) #Incr of Load at this step. IncrLoad = Loads_To_Apply * IncrStage
        IncrDispl = np.zeros((3*S0.NodesCount,1))  #Incr of Displacement at this step. IncrDispl = v * IncrStage
        IncrN = np.zeros((S0.ElementsCount,1)) #Incr of AxialForce at this step. IncrN = N * IncrStage
        IncrR = np.zeros((S0.FixationsCount,1)) #Incr of Reaction at this step. IncrR = R * IncrStage

        # Stage 0
        Stages = np.array([Stage]) #succesion of stages
        StagesLoad = IncrLoad.copy() #list of applied load at all stages.
        StagesDispl = IncrDispl.copy() #list of Displacement at all stages.
        StagesN = AxialForcesInit.copy() #list of AxialForces at all stages.
        StagesR = IncrR.copy() #list of Reactions at all stages.

        while (Stage < 1 and k < Max_n_steps):

            # A new initial structure is considered at each step. A Linear Solve method is applied on it.
            CurDispl = StagesDispl[:,k].reshape((-1,1))
            CurNodesCoord = NodesCoord0 + CurDispl
            CurAxialForces = StagesN[:,k].reshape((-1,1))
            cur = S0.NewStructureObj(CurNodesCoord, CurAxialForces, p)

            try:
                (v, N, R) = cur.LinearSolve_Displ_Method(cur.Nodes_coord, cur.AxialForces_Already_Applied, cur.Loads_To_Apply)
            except np.linalg.LinAlgError:
                # print("la matrice est singulière")
                NodesCoord_perturbed = cur.Perturbation(cur.Nodes_coord, cur.IsDOFfree, perturb)
                (v, N, R) = cur.LinearSolve_Displ_Method(NodesCoord_perturbed,cur.AxialForces_Already_Applied,cur.Loads_To_Apply)
            finally:
                cur.Displacements_Results = v #Linear results
                cur.AxialForces_Results = N
                cur.Reactions_Results = R

                if k==0: # Initial Structure = current at first step
                    S0.Elements_L = cur.Elements_L
                    S0.Elements_Cos = cur.Elements_Cos
                    S0.K_constrained = cur.K_constrained

                if l0 == 1:  # if incremental length = 1
                    IncrStage = 1  #final stage is obtained in one step. NonLinear Method = Linear Method

                else:  # use arclength constrain
                    norm = (v.transpose() @ v)[0,0] #scalar product
                    f = np.sqrt(1 + norm) #scalar
                    IncrStage = (l0 / f) * np.sign(np.dot(p.transpose(), v))[0,0]  # it can be negative

                if Stage + IncrStage > 1:  # Ensure to stop exactly on Final Stage = 1.
                    IncrStage = 1 - Stage

                # Move to next step
                Stage = Stage + IncrStage
                IncrLoad = p * IncrStage
                IncrDispl = v * IncrStage
                IncrN = N * IncrStage
                IncrR = R * IncrStage

                #store the results of this stage
                Stages = np.hstack((Stages,Stage))
                StagesLoad= np.hstack((StagesLoad,StagesLoad[:,k].reshape((-1,1)) + IncrLoad))
                StagesDispl= np.hstack((StagesDispl,StagesDispl[:,k].reshape((-1,1)) + IncrDispl))
                StagesN = np.hstack((StagesN,StagesN[:,k].reshape((-1,1)) + IncrN))
                StagesR= np.hstack((StagesR,StagesR[:,k].reshape((-1,1)) + IncrR))

                k = k + 1

        if k == Max_n_steps:
            # print('nbr iterations du solveur non linéaire : {}/{}  progression Stage: {} %'.format(k, Max_n_steps,np.around(Stage * 100,decimals=2)))
            return (np.array([[]]),np.array([[]]),np.array([[]]),np.array([[]]),np.array([[]]))
        else:
            # print('nbr iterations du solveur non linéaire :', k)
            return (Stages,StagesLoad,StagesDispl,StagesN,StagesR)

    # endregion

    # region Linear Solve by Force Method

    def Core_LinearSolve_Force_Method(S0):
        """

        :return:
        """
        S0.C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.Elements_EndNodes)
        (S0.Elements_L0,S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.Nodes_coord, S0.C)
        (S0.A, S0.A_free, S0.A_fixed) = S0.Compute_Equilibrium_Matrix(S0.Elements_Cos0,S0.C,S0.IsDOFfree)

        d0 = np.zeros((3*S0.NodesCount,1)) #initial displacements
        t0 = S0.AxialForces_Already_Applied #initial forces at first step
        p0 = S0.Loads_Already_Applied[S0.IsDOFfree] #initial load already applied on the structure

        p_ToApply = S0.Loads_To_Apply[S0.IsDOFfree] #external point loads to apply on the free dofs
        e_ToApply = S0.Elongations_To_Apply  #elongations to apply

        dp_free = p_ToApply + p0 - S0.A_free @ t0 #unbalanced loads. A_free @ t0 should be equal to p0 if the initial structure is in equilibrium.

        ## 0) Compute the SVD of At
        SVD = S0.SVD_Equilibrium_Matrix(S0.A_free)

        ## 1) Solve Equilibrium A @ dt = dp   to find the increment of tensions dt due to unbalanced load and external elongations
        S0.F = S0.Flexibility_Matrix(S0.Elements_E,S0.Elements_A,S0.Elements_L0)
        (dt, de) = S0.Equilibrium_Analysis(SVD,S0.F,dp_free,e_ToApply)

        ## 2) Solve Compatibility Bt @ dd = de to find the increment of displacements dd due to unbalanced loads and external elongations
        G = S0.Geometric_Loads_Matrix(SVD,t0)
        dd_free = S0.Compatibility_Analysis(SVD,G,de)
        dd = np.zeros((3 * S0.NodesCount, 1))
        dd[S0.IsDOFfree] = dd_free

        S0.AxialForces_Results = dt
        S0.Displacements_Results = dd


    def Flexibility_Matrix(S0,Elements_E,Elements_A,Elements_L0):
        L_diag = np.diag(Elements_L0)
        A_inv_diag = np.diag(1/Elements_A.reshape(-1,))
        E_inv_diag = np.diag(1 / Elements_E.reshape(-1,))
        F = L_diag @ A_inv_diag @ E_inv_diag
        return F

    def Geometric_Loads_Matrix(S0,SVD,t0):
        """
        La matrice G (size Ndof x m) contient les Charges nécessaires pour activer chaque mécanisme d'une unité.
        On actionne chaque mécanisme de la structure avec un déplacement d'une unité et on forme la matrice G.
        Hypothèse : approximation linéaire : la longueur et la tension de chaque élément ne varient pas
        :param config:
        :return:
        """
        t0  = t0.reshape(-1,)
        G = np.zeros((S0.DOFfreeCount, SVD.m))
        for i in np.arange(SVD.m):

            Um_i = (SVD.Um_row[i, :]).transpose() #(3nodes,1)  Mechanism i is actionned by a unit displacement
            Elements_Cos_Displ = S0.Compute_Elements_Reorientation(Um_i, S0.C, S0.Elements_L0)
            (A_nl, A_nl_free, A_nl_fixed) = S0.Compute_NL_Equilibrium_Matrix(Elements_Cos_Displ, S0.C, S0.IsDOFfree)
            G_i = A_nl_free @ t0
            G[:,i] = G_i

        # S0.Kg_mod = S0.Um_t @ G
        # S0.Kg = G @ S0.Um_t
        # print(G)
        return G

    def Compute_Elements_Reorientation(S0,Displacements,C,Elements_L0):
        """
        Calculates the Lines properties (Lengths, CosDir) based on the given Nodes_coord and Connectivity Matrix C, and store it in S0
        """
        assert C.shape==(S0.ElementsCount,S0.NodesCount),"check that shape of connectivity matrix C = (nbr lines, nbr nodes)"

        # get the current displacement dX, dY or dZ of all nodes
        Displ_3 = Displacements.reshape((-1,3))
        dX = Displ_3[:, 0]  # (nbr nodes,)
        dY = Displ_3[:, 1]
        dZ = Displ_3[:, 2]

        # calculate the différence of displacements between both extremities of each line
        D_dX = C @ dX  # gives dX1-dX0 for each line
        D_dY = C @ dY  # (nbr lines,) = (nbr lines, nbr nodes) @ (nbr nodes,)
        D_dZ = C @ dZ

        # calculate the initial length of each line
        Diag_L0_inv = np.diag(1 / Elements_L0)  # (nbr lines, nbr lines) where only the diagonal is non nul

        # calculate the initial cos directors of each line
        Cos_dX = Diag_L0_inv @ D_dX  # (nbr lines,)  = (nbr lines, nbr lines) @ (nbr lines,)
        Cos_dY = Diag_L0_inv @ D_dY
        Cos_dZ = Diag_L0_inv @ D_dZ

        Elements_Cos_Displ = np.hstack((Cos_dX.reshape((-1,1)),Cos_dY.reshape((-1,1)),Cos_dZ.reshape((-1,1)))) # (nbr lines,3)

        return (Elements_Cos_Displ)

    def Compute_NL_Equilibrium_Matrix(S0,Elements_Cos_Displ,C,IsDOFfree):
        """
        :return: Calculate the non linear equilibrium matrix based on the cos of the current displacements (dx1-dx0)/l0
        """

        (b,n) = C.shape #(nbr lines, nbr nodes)
        C_t = C.transpose()

        Cos_dX = Elements_Cos_Displ[:,0]
        Cos_dY = Elements_Cos_Displ[:,1]
        Cos_dZ = Elements_Cos_Displ[:,2]

        # 2) calculate equilibrium matrix
        # for each node (corresponding to one row), if the line (corresponding to a column) is connected to the node, then the entry of A contains the cos director, else 0.
        Ax = C_t @ np.diag(Cos_dX)  # (nbr nodes, nbr lines)  =  (nbr nodes, nbr lines) @ (nbr lines, nbr lines)
        Ay = C_t @ np.diag(Cos_dY)
        Az = C_t @ np.diag(Cos_dZ)

        A = np.zeros((3 * n, b)) # (3*nbr nodes, nbr lines)

        # the dof are sorted like this [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        for i in range(n):
            A[3 * i, :] = Ax[i, :]
            A[3 * i + 1, :] = Ay[i, :]
            A[3 * i + 2, :] = Az[i, :]

        A_free = A[IsDOFfree]  # (nbr free dof, nbr lines)
        A_fixed = A[~IsDOFfree] # (nbr fixed dof, nbr lines)

        return (A,A_free,A_fixed)

    def Equilibrium_Analysis(S0, SVD, F, dp_free, e_ToApply):
        """
        L'analyse de l'équilibre est effectuée en coordonnées modales plutôt que coordonnées XYZ de chaque noeud. dp_free are the unbalanced loads to apply on the free dof. e_ToApply are the external elongations to apply (prestress loads)
        :param
        :return:
        """
        r = SVD.r
        m = SVD.m
        Sr = np.diag(SVD.Sr)

        ## tensions in the isostatic structure
        dp_r_mod = SVD.Ur_free_row @ dp_free # extensionnal unbalanced loads in modal coordinates
        dt_r_mod = np.linalg.solve(Sr, dp_r_mod) # additionnal tensions in modal coordinates due to extensionnal unbalanced loads
        Vr  = SVD.Vr_row.transpose()
        dt_r = Vr @ dt_r_mod # additional tensions in global coordinates
        de_r = F @ dt_r #additional elongations in global coordinates coming from external elongations to apply


        ## tensions in the hypertstatic structure
        e_proj = SVD.Vs_row @ (e_ToApply + de_r) #extensional elongations are projected onto the space of self-stress modes. Indeed, extensional elongations may activate a self-stress mode. e_proj are the coordinates of the activated self-stress modes.
        Vs = SVD.Vs_row.transpose()
        F_mod = SVD.Vs_row @ F @ Vs
        alpha = np.linalg.solve(F_mod, -e_proj) #the hyperstatic unknowns OR the levels of self-stress OR the modal coordinates of the self-stress modes Vs
        dt_s = Vs @ alpha #the hyperstatic tensions
        de_s = F @ dt_s #the hyperstatic elongations

        dt = dt_r + dt_s # the additional tensions coming from the unbalanced loads and the external elongations to apply
        de = e_ToApply + de_r + de_s #

        return (dt,de)

    def Compatibility_Analysis(S0,SVD,G,de):
        dd = np.zeros((3 * S0.NodesCount, 1))  # displacements at first step
        Ur_free = SVD.Ur_free_row.transpose() #(dof_free,r)
        Um_free = SVD.Um_free_row.transpose() #(dof_free,m)
        Sr = np.diag(SVD.Sr)

        # kinematically determinate displacements
        de_mod = SVD.Vr_row @ de #additional elongations in modal coordinates (r,1) coming from external elongations e_ToApply + elongations coming from unbalanced loads
        dd_r_mod = np.linalg.solve(Sr, de_mod) #(r,1)
        dd_r = Ur_free @ dd_r_mod #(dof_free,1) the displacements due to the elongations

        # kinematically indeterminate displacements
        G_row = G.transpose() #(m,dof_free) geometric_loads_matrix
        b = G_row @ dd_r #(m,1) work produced by the geometric_loads (required loads to activate a mechanism by 1 unity) displaced by kinematically determinate  displacement
        Bm = G_row @ Um_free #(m,m) work produced by the geometric_loads displaced by kinematically indeterminate displacement
        beta = np.linalg.solve(Bm, -b) #(m,1) the kinematic unknowns Or the modal coordinates associated with the mechanism modes
        dd_m = Um_free @ beta #(dof_free,1) the displacements due to the activation of the mechanisms

        dd = dd_r + dd_m # the total displacements

        return dd
    # endregion



    # region Non Linear Solve by Force Method
    def Core_NonLinearSolve_Force_Method(S0):
        """
        :return:
        """
        S0.C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.Elements_EndNodes)
        (S0.Elements_L0, S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.Nodes_coord, S0.C)
        (S0.A, S0.A_free, S0.A_fixed) = S0.Compute_Equilibrium_Matrix(S0.Elements_Cos0, S0.C, S0.IsDOFfree)
        S0.F = S0.Flexibility_Matrix(S0.Elements_E, S0.Elements_A, S0.Elements_L0)

        (t,d) = S0.NonLinearSolve_Force_Method(S0.n_steps, S0.Loads_Already_Applied, S0.AxialForces_Already_Applied, S0.Loads_To_Apply, S0.Elongations_To_Apply)

        S0.AxialForces_Results = t
        S0.Displacements_Results = d

    def NonLinearSolve_Force_Method(S0,Max_n_steps, Loads_Already_Applied, AxialForces_Already_Applied, Loads_To_Apply, Elongations_To_Apply):
        """
        Non linear solve of the structure. Input:
            NodesCoord0: Initial Nodes coordinates (Nx3)
            AxialForces_Already_Applied: Initial AxialForces in equilibrium in the structure (Bx1)
            Loads_To_Apply: Loads to apply on the nodes (Nx3)
        """
        d0 = np.zeros((3 * S0.NodesCount, 1))  # initial displacements
        t0 = AxialForces_Already_Applied.reshape(-1,1)  # initial forces at first step
        p0 = Loads_Already_Applied[S0.IsDOFfree]  # initial load already applied on the structure

        k = 1
        kmax = Max_n_steps
        err = 1
        tol = 1e-5

        p_ToApply = Loads_To_Apply[S0.IsDOFfree].reshape((-1,1))
        e_ToApply = Elongations_To_Apply.reshape((-1,1))

        dp_free = np.zeros((S0.DOFfreeCount,1)) #Increment of Load at this step.
        dd = np.zeros((3*S0.NodesCount,1))  #Incr of Displacement at this step.
        dt = np.zeros((S0.ElementsCount,1)) #Incr of AxialForce at this step.
        # IncrR = np.zeros((S0.FixationsCount,1)) #Incr of Reaction at this step.

        # Stage 0
        d = d0.copy() #list of Displacement at all stages k.
        t = t0.copy() #list of AxialForces at all stages k.
        # StagesR = IncrR.copy() #list of Reactions at all stages.

        while (k <= kmax and err>= tol):

            # A new initial structure is considered at each step. A Linear Solve method is applied on it.
            Prev_d = d[:, k-1].reshape((-1, 1))
            Prev_t = t[:,k-1].reshape((-1,1))

            Elements_Cos_Displ = S0.Compute_Elements_Reorientation(Prev_d, S0.C, S0.Elements_L0)
            (A_nl, A_nl_free, A_nl_fixed) = S0.Compute_NL_Equilibrium_Matrix(Elements_Cos_Displ, S0.C, S0.IsDOFfree)
            A_t = S0.A+A_nl
            A_t_free = S0.A_free + A_nl_free

            dp_free = p_ToApply + p0 - A_t_free @ Prev_t  # unbalanced loads. A_free @ t0 should be equal to p0 if the initial structure is in equilibrium.

            ## 0) Compute the SVD of At
            SVD = S0.SVD_Equilibrium_Matrix(A_t_free)

            ## 1) Solve Equilibrium A @ dt = dp   to find the increment of tensions dt due to unbalanced load and external elongations
            if k!=1 :
                e_ToApply = np.zeros((S0.ElementsCount,1))
            (dt, de) = S0.Equilibrium_Analysis(SVD, S0.F, dp_free, e_ToApply)

            ## 2) Solve Compatibility Bt @ dd = de to find the increment of displacements dd due to unbalanced loads and external elongations

            # de = de - A_t.transpose() @ Prev_d # the unbalanced elongations
            G = S0.Geometric_Loads_Matrix(SVD, Prev_t)
            dd_free = S0.Compatibility_Analysis(SVD, G, de)
            dd[S0.IsDOFfree] = dd_free

            #store the results of this stage
            d = np.hstack((d,d[:,k-1].reshape((-1,1)) + dd))
            t = np.hstack((t,t[:,k-1].reshape((-1,1)) + dt))

            p_norm = np.linalg.norm(p_ToApply)
            if (p_norm <= 1e-4) :
                err = np.linalg.norm(dd) / np.linalg.norm(d[:,k])
            else :
                err = np.linalg.norm(dp_free) / np.linalg.norm(p_ToApply)
            print(err)
            k = k + 1

        if k == kmax:
            # print('nbr iterations du solveur non linéaire : {}/{}  progression Stage: {} %'.format(k, Max_n_steps,np.around(Stage * 100,decimals=2)))
            return (np.array([[]]),np.array([[]]))
        else:
            # print('nbr iterations du solveur non linéaire :', k)
            return (t[:,k-1],d[:,k-1])






    # endregion




