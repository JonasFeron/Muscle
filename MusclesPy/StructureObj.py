import numpy as np
from data import SharedData

class ResultsSVD():
    """
    This class stores the results into a ResultsSVD object of the Singular Value Decomposition of the Equilibrium Matrix of the structure in the current state.
    Ref: Pellegrino, 1993, Structural computations with the singular value decomposition of the equilibrium matrix
    """

    def __init__(SVD,NodesCount = 0,ElementsCount = 0,FixationsCount = 0):
        """
        Initialize an empty ResultsSVD object ready to store the results
        :param NodesCount: number of nodes
        :param ElementsCount: number of elements
        :param FixationsCount: number of fixed degrees of freedom
        """
        DOFfreeCount = 3*NodesCount - FixationsCount

        SVD.S = np.zeros((DOFfreeCount,)) #eigen values of AFree
        SVD.r = 0  # number of non null eigen value. rank of AFree
        SVD.Sr = np.zeros((SVD.r,)) #non null eigen values of AFree

        SVD.s = ElementsCount - SVD.r #degree of static indeterminacy = nbr of self-stress modes
        SVD.Vr_row = np.zeros((SVD.r, ElementsCount)) # r row eigen vectors. Interpretation: Bar tensions in equilibrium with the Diag(S)* Loads of Ur OR Bar elongations compatible with Diag(1/S) * Extensional displacements of Ur
        SVD.Vs_row = np.zeros((SVD.s, ElementsCount)) # s row eigen vectors. Interpretation: Cur-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
        SVD.SS = np.zeros((SVD.s, ElementsCount))  # s row eigen vectors. =Vs_row but rescaled to have the biggest force = -1 (compression) in each vector. Interpretation: rescaled Cur-stress modes

        SVD.m = DOFfreeCount - SVD.r #degree of kinematic indeterminacy = nbr of mechanisms
        SVD.Ur_row = np.zeros((SVD.r, 3 * NodesCount)) #same as free but considering 0 reaction/displacement at the support.
        SVD.Ur_free_row = np.zeros((SVD.r, DOFfreeCount)) # r row eigenvectors. Interpretation: Loads which can be equilibrated in the current struct OR Extensional displacements
        SVD.Um_row = np.zeros((SVD.m, 3 * NodesCount)) #same as free but considering 0 reaction/displacement at the support.
        SVD.Um_free_row = np.zeros((SVD.m, DOFfreeCount)) # m row eigenvectors. Interpretation: Loads which can not be equilibrated in the current struct OR Inextensional displacements (sol of B@d = 0)

    def PopulateWith(SVD,S,r,Sr,s,Vr_row,Vs_row,SS,m,Ur_row,Ur_free_row,Um_row,Um_free_row):
        """
        Fill in the ResultsSVD object with the obtained results
        :param S:
        :param r:
        :param Sr:
        :param s:
        :param Vr_row:
        :param Vs_row:
        :param SS:
        :param m:
        :param Ur_row:
        :param Ur_free_row:
        :param Um_row:
        :param Um_free_row:
        """
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

    def SVDEquilibriumMatrix(SVD, S, AFree):
        """
        Compute the Singular Value Decomposition of the Equilibrium Matrix of the structure
        :param S: The structure object
        :param AFree: The Equilibrium Matrix. shape (DOFfreeCount, ElementsCount)
        :return: The resulting (eigen) vectors of the Equilibrium Matrix decomposition
        """
        # 1) retrieve and check inputs
        ElementsCount = S.ElementsCount
        NodesCount = S.NodesCount
        DOFfreeCount = S.DOFfreeCount
        IsDOFfree = S.IsDOFfree

        assert AFree.shape == (DOFfreeCount, ElementsCount), "Please check the equilibrium matrix (AFree) shape"
        assert np.abs(AFree).sum() != 0, "Please check that the equilibrium matrix (AFree) has been computed"

        #Note the following notation:
        #Free if the dimension(s) of the vector/matrix correspond to the number of free degrees of freedom (DOFfreeCount)
        #Row if the eigen vectors are horizontal
        #Col if the eigen vectors are vertical
        #We only store the Row eigenvectors. Please transpose the matrice to obtain the Col eigenvectors.

        # 2) calculate the eigenvalues and vectors
        U_free_col, S, V_row = np.linalg.svd(AFree)  # S contains the eigen values of AFree in decreasing order. U_col is a matrix (nbr free DOF,nbr free DOF) containing the column eigen vectors. V_row is a matrix (nbr lines,nbr lines) containing the row eigen vectors.

        Lambda_1 = S.max()
        Tol = Lambda_1 * 10 ** -3  # Tol is the limit below which an eigen value is considered as null.
        Sr = S[S >= Tol]  # non null eigen values
        r = Sr.size  #number of non null eigen value. rank of AFree
        m = DOFfreeCount - r  #degree of kinematic indeterminacy = nbr of mechanisms
        s = ElementsCount - r  #degree of static indeterminacy = nbr of self-stress modes

        # 3a) Interprete the eigenVectors in the elements space
        Vr_row = V_row[:r,:]  # r row eigen vectors (,nbr lines). Interpretation: Bar tensions in equilibrium with the Diag(S)* Loads of Ur OR Bar elongations compatible with Diag(1/S) * Extensional displacements of Ur
        Vs_row = np.zeros((s, ElementsCount)) # s row eigen vectors. Interpretation: Cur-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
        SS = np.zeros((s, ElementsCount)) # s row eigen vectors. =Vs_row but rescaled to have the biggest force = -1 (compression) in each vector. Interpretation: rescaled Cur-stress modes

        if s != 0: #rescale the eigen vectors Vs_row such that the highest value = -1 (compression) and store the results in the Cur-Stress mode matrix SS.
            Vs_row = V_row[-s:,:]  # s Vecteurs (lignes) propres (associés aux VaP nulles) de longueur ElementsCount. Interprétations : Cur-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
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

        SVD.PopulateWith(S, r, Sr, s, Vr_row, Vs_row, SS, m, Ur_row, Ur_free_row, Um_row, Um_free_row)

class State():
    def __init__(Cur, S=None, nodesCoord=np.zeros((0,)), loads=np.zeros((0,)), tension=np.zeros((0,)), reactions=np.zeros((0,))):
        """
        The Current State of a Structure Object S is defined by
        :param NodesCoord: The current nodes coordinates of the structure
        :param Loads: The total loads currently applied on the structure
        :param Tension: The internal tension forces currently existing in the structure
        :param Reactions: The reactions forces currently applied on the structure by the structure fixations
        """
        ##### State inputs #####

        if isinstance(S, StructureObj):
            Cur.S = S # the structure object in the current state
        else :
            Cur.S = StructureObj()
        Cur.NodesCoord = nodesCoord.reshape((-1,))
        Cur.Loads = loads.reshape((-1,))
        Cur.Tension = tension.reshape((-1,))
        Cur.Reactions = reactions.reshape((-1,))


        ##### Initialize the State properties #####
        Cur.ElementsL = np.zeros((S.ElementsCount,)) #Elements lengths
        Cur.ElementsCos = np.zeros((S.ElementsCount, 3)) #The cosinus directors of the elements
        Cur.A = np.zeros((3 * S.NodesCount, S.ElementsCount)) #The equilibrium matrix of the structure in the current state
        Cur.AFree = np.zeros((S.DOFfreeCount, S.ElementsCount))  # Equilibrium matrix of the free degrees of freedom only
        Cur.AFixed = np.zeros((S.FixationsCount, S.ElementsCount))  # Equilibrium matrix of the fixed degrees of freedom only. Allows to find reactions from tension forces. AFixed @ Tension = Reaction
        Cur.SVD = ResultsSVD() #An empty results SVD object

        Cur.Residual = np.ones((3 * S.NodesCount,)) # the unbalanced loads = All external Loads - A @ Tension
        Cur.IsInEquilibrium = False # the current state of the structure is in equilibrum if the unbalanced loads (Residual) are below a certain threshold (very small)

    def ComputeElementsLengthsAndCos(Cur, NodesCoord, C):
        """
        Calculates the Lines properties (Lengths, Cos) based on the given NodesCoord and Connectivity Matrix C
        """
        
        # Check inputs
        assert C.shape == (Cur.S.ElementsCount, Cur.S.NodesCount), "Please check the shape of the connectivity matrix C"

        # Get the current X, Y or Z coordinates of all nodes
        NodesCoordXYZ = NodesCoord.reshape((-1,3)) # shape (NodesCount,3) instead of (3*NodesCount,)
        X = NodesCoordXYZ[:, 0] # shape (NodesCount,)
        Y = NodesCoordXYZ[:, 1]
        Z = NodesCoordXYZ[:, 2]

        # Compute the différence of coordinates between both ends of each line
        DX = C @ X  # return X1-X0 for each line
        DY = C @ Y  # shape (ElementsCount,) = (ElementsCount, NodesCount) @ (NodesCount,)
        DZ = C @ Z

        # Compute the current lengths of each line
        ElementsL = np.sqrt(DX ** 2 + DY ** 2 + DZ ** 2)  # (ElementsCount,)
        Diag1overL = np.diag(1 / ElementsL)  # shape (ElementsCount, ElementsCount) where only the diagonal is non nul

        # Compute the current cosinus directors of each line
        CosX = Diag1overL @ DX  # shape (ElementsCount,)  = (ElementsCount, ElementsCount) @ (ElementsCount,)
        CosY = Diag1overL @ DY
        CosZ = Diag1overL @ DZ

        ElementsCos = np.hstack((CosX.reshape((-1,1)),CosY.reshape((-1,1)),CosZ.reshape((-1,1)))) # shape (ElementsCount,3)

        return (ElementsL,ElementsCos)

    def ComputeEquilibriumMatrix(Cur, C, IsDOFfree, ElementsCos):
        """
        :return: Compute the equilibrium matrix of the structure in its current state based on the current cosinus director of the elements and on the supports conidtions.
        """

        (ElementsCount,NodesCount) = C.shape

        CosX = ElementsCos[:, 0]
        CosY = ElementsCos[:, 1]
        CosZ = ElementsCos[:, 2]

        # 2) calculate equilibrium matrix
        # for each node (corresponding to one row), if the line (corresponding to a column) is connected to the node, then the entry of A contains the cos director, else 0.
        Ax = C.T @ np.diag(CosX)  # (NodesCount, ElementsCount)  =  (NodesCount, ElementsCount) @ (ElementsCount, ElementsCount)
        Ay = C.T @ np.diag(CosY)
        Az = C.T @ np.diag(CosZ)

        A = np.zeros((3 * NodesCount, ElementsCount)) # (3*nbr nodes, nbr lines)

        # the Degrees Of Freedom are sorted like this [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        for i in range(NodesCount):
            A[3 * i, :] = Ax[i, :]
            A[3 * i + 1, :] = Ay[i, :]
            A[3 * i + 2, :] = Az[i, :]

        A_free = A[IsDOFfree]  # (nbr free dof, ElementsCount)
        A_fixed = A[~IsDOFfree] # (nbr fixed dof, ElementsCount)

        return (A,A_free,A_fixed)

    def ComputeSVD(Cur, AFree):
        """
        :param AFree: The Equilibrium Matrix with shape (DOFfreeCount, ElementsCount)
        :return: the ResultsSVD object in the current state is filled with the results of the singular value decomposition of AFree
        """
        Cur.SVD.SVDEquilibriumMatrix(Cur.S, AFree) #Compute and store the results of the singular value decompositon of AFree in the current state
        return Cur.SVD

    def ComputeTension(Cur,ElementsLCur,ElementsLFree,ElementsE,ElementsA):
        """

        :param ElementsLCur: Current lengths of the elements. shape (ElementsCount,).
        :param ElementsLFree: Free lengths of the elements. shape (ElementsCount,).
        :param ElementsE: Young modules of the elements if in compression or if in tension. [EinComp, EinTens]. shape (ElementsCount, 2).
        :param ElementsA: Area of the elements if in compression or if in tension. [AinComp, AinTens]. shape (ElementsCount, 2).
        :return: T, the tension forces in each elements. shape (ElementsCount,).
        """

        # TensionApplied = np.zeros((0,))
        # assert TensionApplied.size == ElementsCount or TensionApplied.size == 0 , "Please check the shape of TensionApplied"

        #1) Check the inputs

        ElementsCount = Cur.S.ElementsCount
        assert ElementsLCur.shape == (ElementsCount,), "Please check the shape of ElementsLCur"
        assert ElementsLFree.shape == (ElementsCount,), "Please check the shape of ElementsL0"
        assert ElementsE.shape == (ElementsCount,2), "Please check the shape of ElementsE"
        assert ElementsA.shape == (ElementsCount,2), "Please check the shape of ElementsA"

        #2) Check the state of the elements (in compression or in tension) and find their associated stiffness

        #For each elements, there is one E value in case of compression and another value in case of tension. Idem for A
        #For instance, the Young modulus of a cable could be 0 in compression and 100e3 MPa in tension.
        #In this case, the cable vanish from stiffness matrix if it slacks

        EinCompression = ElementsE[:,0]
        EinTension = ElementsE[:,1]
        AinCompression = ElementsA[:,0]
        AinTension = ElementsA[:,1]

        DeltaL = ElementsLCur-ElementsLFree
        IsElementInTension = DeltaL>=0 #elements are in tension if they are longer than before assembly

        E = np.where(IsElementInTension,EinTension,EinCompression) #the Young modulus of the elements in the current state (depending if compression or tension)
        A = np.where(IsElementInTension, AinTension, AinCompression) #the Area of the elements in the current state (depending if compression or tension)

        #3) Compute the elements flexibility L/EA and stiffness EA/L

        F = Cur.S.Flexibility(E,A,ElementsLFree) # shape (ElementsCount,). Important to note that the Free lengths are considered in the flexibility
        Kbsc = 1/F # shape (ElementsCount,). basic material stiffness vector of each individual element

        #4) Compute the tension

        T = Kbsc*DeltaL # shape (ElementsCount,)  T = EA/Lfree * (Lcur - Lfree)
        return T

    def ComputeResidual(Cur,A,Loads,Tension):
        """
        Returns the Residual (=unbalanced loads) considering the equilibrium equation R = Loads - A @ Tension.
        If A=A with shape(3 NodesCount,ElementsCount), the Residual = the Reaction where the DOF are fixed.
        If A=Afree with shape (DOFfreeCount,ElementsCount), the Residual = 0 where the DOF are fixed.

        :param A: [/] - (3*NodesCount,ElementsCount) OR (DOFfreeCount,ElementsCount) depending if A=A or A=Afree - the equilibrium matrix of the structure.
        :param Loads: [N] - shape (3*NodesCount,) - The total external load acting in the current state.
        :param Tension: [N] - shape (ElementsCount,) - The total internal forces acting in the elements in the current state.
        :return: Residual: [N] - shape (3*NodesCount,) whatever the shape of A -  The unbalanced loads.
        """

        #1) Check the inputs
        NodesCount = Cur.S.NodesCount
        ElementsCount = Cur.S.ElementsCount
        DOFfreeCount = Cur.S.DOFfreeCount
        IsDOFfree = Cur.S.IsDOFfree
        assert A.shape == (3*NodesCount,ElementsCount) or A.shape == (DOFfreeCount,ElementsCount), "Please check the shape of A"
        assert Loads.size == 3*NodesCount, "Please check the shape of Loads"
        assert Tension.size == ElementsCount, "Please check the shape of Tension"
        assert IsDOFfree.size == 3*NodesCount, "Please check the shape of IsDOFfree"
        #2) Check if A=A or A=Afree
        DOF2Compute = np.ones((3*NodesCount,),dtype=bool) #a vector of true. if true, the residual is computed. if false, the residual = 0.
        if A.shape == (DOFfreeCount, ElementsCount): #if A=Afree
            DOF2Compute = IsDOFfree.reshape(-1,) # then Compute the Residual only for the free DOF and impose Residual=0 for the fixed DOF.

        #3) Compute the Residual
        Residual = np.zeros((3*NodesCount,))
        R = Residual[DOF2Compute]
        T = Tension.reshape(-1,)
        L = Loads.reshape(-1,)[DOF2Compute]

        R = L - A @ T # equilibrium equations such that A @ T = L if equilibrium.
        Residual[DOF2Compute] = R #the Residual is computed everywherer (if A=A) or only for the free DOF (if A=Afree).

        return Residual

    def ComputeFlexibility(Cur, ElementsE, ElementsA, ElementsL):
        """
        Returns the flexibility L/EA of the elements (considering a possible infinite flexibility = no stiffness)
        :param ElementsE: the young modulus in [MPa] of the elements. shape (ElementsCount,)
        :param ElementsA: the area in [mm²] of the elements. shape (ElementsCount,)
        :param ElementsL: the lengths (free or current) in [m] of the elements. shape (ElementsCount,)
        :return: F : the flexibility L/EA of the elements. shape (ElementsCount,)
        """
        #0) Check the inputs
        assert ElementsE.size == Cur.S.ElementsCount, "Please check the shape of ElementsE"
        assert ElementsA.size == Cur.S.ElementsCount, "Please check the shape of ElementsA"
        assert ElementsL.size == Cur.S.ElementsCount, "Please check the shape of ElementsL"
        E = ElementsE.reshape(-1,)
        A = ElementsA.reshape(-1,)
        L = ElementsL.reshape(-1,)

        #1) Find the slack clables, they have a 0 stiffness, hence infinite flexibility

        NoStiffnessElementsIndex = np.where(np.logical_or(E <= 1e-4 ,A <= 1e-4))

        A[NoStiffnessElementsIndex] = 1 #to avoid to divide by 0 later
        E[NoStiffnessElementsIndex] = 1  # to avoid to divide by 0 later

        #2) Compute the flexibility
        F = L/(E*A)
        F[NoStiffnessElementsIndex] = 1e6 # [m/N] elements with 0 stiffness have an infinite flexibility
        return F

    def ComputeMaterialStiffnessMatrix(Cur,A,Flexibility):
        """
        Compute the material stiffness matrix of the structure in the current state given the equilibrium matrix and the flexibilities in the current state
        :param A: [/] - shape (3*NodesCount,ElementsCount) - The equilibrium matrix of the structure in the current state
        :param Flexibility: [m/N] - shape (ElementsCount,) - The flexibility vector L/EA for each element in the current state
        :return: Kmat : [N/m] - shape(3*NodesCount,3*NodesCount) - the material stiffness matrix of the structure in the current state
        """
        ElementsCount = Cur.S.ElementsCount
        NodesCount = Cur.S.NodesCount
        DOFfreeCount = Cur.S.DOFfreeCount

        assert A.shape == (3*NodesCount,ElementsCount) or A.shape == (DOFfreeCount,ElementsCount), "Please check the shape of A"
        assert Flexibility.size == ElementsCount, "Please check the shape of the Flexibility vector"

        F = Flexibility.reshape(-1,)
        Kbsc = np.diag(1/F) # EA/L in a diagonal matrix. Note that EA/L can be equal to 0 if the cable is slacked
        B = A.T # The compatibility matrix is the linear application which transforms the displacements into elongation.
        Kmat = A @ Kbsc @ B # (3*NodesCount,3*NodesCount) OR (DOFfreeCount, DOFfreeCount)

        return Kmat

    def ComputeForceDensities(Cur,CurTension,CurElementsL):
        """
        Compute the force densities
        :param CurTension: [N] - shape (ElementsCount,) - The current tension forces in the elements
        :param CurElementsL: [m] - shape (ElementsCount,) - The current lengths of the elements
        :return: q : [N/m] - shape (ElementsCount,) - The force densities q= T/L
        """
        #References:
        # Sheck, 1974, The force density method for formfinding and computation of networks
        # Vassart, Motro, 1999, Multiparametered Formfinding Method: Application to Tensegrity Systems

        #1) Check inputs
        ElementsCount = Cur.S.ElementsCount
        assert CurTension.size == ElementsCount, "Please check the shape of CurTension"
        assert CurElementsL.size == ElementsCount, "Please check the shape of CurTension"
        T = CurTension.reshape(-1,)
        L = CurElementsL.reshape(-1,)
        q = T / L
        return q


    def ComputeGeometricStiffnessMatrix(Cur, C, q):
        """
        :param C: [/] - shape (ElementsCount, NodesCount) - The connectivity matrix
        :param q: [N/m] - shape (ElementsCount,) - The force densities q= T/L
        :return: Kgeo: [N/m] - shape (3*NodesCount,3*NodesCount) - The force densities q= T/L
        """
        #References:
        # Sheck, 1974, The force density method for formfinding and computation of networks
        # Vassart, Motro, 1999, Multiparametered Formfinding Method: Application to Tensegrity Systems
        # Zhang, Ohsaki, 2015, Tensegrity structures: Form, Stability, and Symmetry

        #1) Check the input
        ElementsCount = Cur.S.ElementsCount
        NodesCount = Cur.S.NodesCount
        assert q.size == ElementsCount, "Please check the shape of the force densities q"
        assert C.shape == (ElementsCount,NodesCount), "Please check the shape of the connectivity matrix C"
        Q = np.diag(q.reshape(-1,)) # shape (ElementsCount,ElementsCount) with diagonal entry = qi = Ti/Li

        #2) Stack the degrees of freedoms
        Cxyz = np.zeros((ElementsCount, 3 * NodesCount))
        # the Degrees Of Freedom are sorted like this [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        for i in range(NodesCount):
            Cxyz[:, 3 * i] = C[:,i]
            Cxyz[:, 3 * i + 1] = C[:,i]
            Cxyz[:, 3 * i + 2] = C[:,i]

        #3) Compute the force density Matrices E, EFree and EFixed as per reference Zhang 2015 p45 equation (2.104)
        #To be implemented

        #4) Compute the Geometrical stiffness matrix as per reference Zhang 2015 p109 equation (4.55)
        Kgeo= Cxyz.T @ Q @ Cxyz # shape (3*NodesCount,3*NodesCount) = (3*NodesCount,ElementsCount) @ (ElementsCount,ElementsCount) @ (ElementsCount,3*NodesCount)

class StructureObj():

    # region Constructors
    def __init__(Self, NodesCount = 0, ElementsCount = 0, FixationsCount = 0):
        """
        Initialize an empty structure. A structure object contains all data which do not vary in time, or in other words, which do not depends on the current state of the structure.
        """
        Self.NodesCount = NodesCount
        Self.ElementsCount = ElementsCount
        Self.FixationsCount = FixationsCount
        Self.DOFfreeCount = 3 * NodesCount - FixationsCount

        ##### Structure informations #####

        Self.Initial = State(Self,np.zeros((3 * Self.NodesCount,))) # Initialize the initial State of the structure.
        #Cur.NodesCoord = np.zeros((3 * Cur.NodesCount,)) #The NodesCoord depend on the Structure State.
        Self.ElementsEndNodes = np.zeros((Self.ElementsCount, 2), dtype=int)
        Self.ElementsLFree = np.zeros((Self.ElementsCount,)) # Lengths of the elements when the elements are free of any tension, or in other words, when the structure is disassemble.
        Self.ElementsA = np.zeros((Self.ElementsCount,))
        Self.ElementsE = np.zeros((Self.ElementsCount,))
        Self.IsDOFfree = np.zeros((3 * Self.NodesCount,), dtype=bool) #the supports conditions

        Self.LoadsApplied = np.zeros((3 * Self.NodesCount,)) #The loads already applied on the structure
        Self.TensionApplied = np.zeros((Self.ElementsCount,)) #The internal tension forces already existing in the structure due to LoadsApplied or to prestress forces
        Self.ReactionsApplied = np.zeros((Self.FixationsCount,)) #The reactions forces already applied on the structure by the structure fixations
        Self.LoadsToApply = np.zeros((3 * Self.NodesCount,)) #The additionnal external loads to apply on the structure
        Self.LengtheningsToApply = np.zeros((Self.ElementsCount,)) #The additionnal lengthenings to impose on the elements free lengths of the structure

        Self.C = np.zeros((Self.ElementsCount, Self.NodesCount), dtype=int) #matrice de connectivité C # (nbr lines, nbr nodes)
        #Cur.Elements_Cos0 = np.zeros((Cur.ElementsCount, 3)) # Cos directors of the elements in the initial structure #(nbr lines,3)
        Self.F = np.eye(Self.ElementsCount, Self.ElementsCount) # Flexibility matrix containing LFree/EA of each element in the diagonal #note that this matrix may be affected if cables slack for instance.

        #Cur.Elements_L = np.zeros((Cur.ElementsCount, 1))  # Lengths of the elements in the current structure. (Initial = Current at the first step of NL Solve)
        #Cur.Elements_Cos = np.zeros((Cur.ElementsCount, 3)) # (nbr lines,3)

        # ##### Assembly informations #####
        # Cur.A = np.zeros((3 * Cur.NodesCount, Cur.ElementsCount)) #Equilibrium matrix
        # Cur.AFree = np.zeros((Cur.DOFfreeCount, Cur.ElementsCount)) #Equilibrium matrix of the free dof only
        # Cur.AFixed = np.zeros((Cur.FixationsCount, Cur.ElementsCount))  # Equilibrium matrix of the fixed dof only. Allows to find reactions from axial forces. AFixed@t=r
        #
        # Cur.SVD = ResultsSVD() #object containing all the results of the Singular Value Decomposition of the Equilibrium matrix

        # =!0 if E and A are non null
        Self.Km = np.zeros((3 * Self.NodesCount, 3 * Self.NodesCount))
        Self.Km_free = np.zeros((Self.DOFfreeCount, Self.DOFfreeCount))

        Self.K_constrained = np.zeros((3 * Self.NodesCount + Self.FixationsCount,
                                       3 * Self.NodesCount + Self.FixationsCount))  # required to solve the structure with imposed displacements of the supports

        # ##### Solve informations #####
        Self.n_steps = 1
        Self.Stages = np.ones((1,))

        Self.Loads_Already_Applied = np.zeros((3 * Self.NodesCount, 1))
        Self.Loads_To_Apply = np.zeros((3 * Self.NodesCount, 1))
        # Cur.Loads_Applied = np.zeros((3*Cur.NodesCount,))
        # Cur.Loads_Total = np.zeros((Cur.NodesCount, 3)) # Already_Applied + To_Apply

        Self.AxialForces_Already_Applied = np.zeros((Self.ElementsCount, 1)) #considered in Geometric stiffness
        Self.AxialForces_Results = np.zeros((Self.ElementsCount, 1)) #results from Loads_To_Apply
        # Cur.AxialForces_Total = np.zeros((Cur.ElementsCount,)) # Results + Already_Applied
        Self.Elongations_To_Apply = np.zeros((Self.ElementsCount, 1))

        # Cur.Displacements_Already_Applied = np.zeros((Cur.NodesCount,3)) # this is such that this.NodesCoord = NodesCoord0 + this.Displacements_Already_Applied. If the structure is solved for the first time,Displacements_Already_Applied =0.
        Self.Displacements_Results = np.zeros((3 * Self.NodesCount, 1)) #results from Loads_To_Apply
        # Cur.Displacements_Total = np.zeros((Cur.NodesCount, 3)) # Results + Already_Applied

        # Cur.Reactions_Already_Applied = np.zeros((Cur.FixationsCount,))
        Self.Reactions_Results = np.zeros((Self.FixationsCount, 1)) #results from Loads_To_Apply
        # Cur.Reactions_Total = np.zeros((Cur.FixationsCount,)) # Results + Already_Applied

        # Cur.AxialForces_To_Apply
        #
        # ##### Calculation Results #####


    # endregion

    # region Public Methods : Main
    def Main_Assemble(S0,Data):
        S0.PopulateWith(Data)
        S0.Core_Assemble()
        S0.SVD = S0.SVD_Equilibrium_Matrix(S0.AFree)

    def test_Main_Assemble(S0, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A=None, Elements_E=None):
        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E)
        S0.Core_Assemble()
        S0.SVD = S0.SVD_Equilibrium_Matrix(S0.AFree)

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
            S0.NodesCoord = NodesCoord.reshape(-1, 1)
        else:
            S0.NodesCoord = None
            S0.NodesCount = -1

        if isinstance(Elements_ExtremitiesIndex, np.ndarray):
            S0.ElementsEndNodes = Elements_ExtremitiesIndex.reshape(-1, 2).astype(int)
            S0.ElementsCount = S0.ElementsEndNodes.shape[0]
        else:
            S0.ElementsEndNodes = None
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
            S0.ElementsA = Elements_A.reshape((-1, 1))
        else:
            S0.ElementsA = np.zeros((S0.ElementsCount, 1))

        if isinstance(Elements_E, np.ndarray) and Elements_E.size == S0.ElementsCount:
            S0.ElementsE = Elements_E.reshape((-1, 1))
        else:
            S0.ElementsE = np.zeros((S0.ElementsCount, 1))

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

    def Core_Assemble(Self):
        """
        Assemble the equilibrim Matrix and the material stiffness matrix. N.B. Do not perfom the SVD -> do it separately
        :return:
        """
        Self.C = Self.ConnectivityMatrix(Self.NodesCount, Self.ElementsCount, Self.ElementsEndNodes)
        (Self.Elements_L, Self.Elements_Cos) = Self.Compute_Elements_Geometry(Self.NodesCoord, Self.C)
        (Self.A, Self.AFree, Self.AFixed) = Self.Compute_Equilibrium_Matrix(Self.Elements_Cos, Self.C, Self.IsDOFfree)
        # if Cur.ElementsA.sum()!=0 and Cur.ElementsE.sum()!=0:
        #     Cur.Km = Cur.Compute_StiffnessMat_Matrix(Cur.A, Cur.ElementsL, Cur.ElementsA, Cur.ElementsE)
        #     Cur.Km_free = Cur.Compute_StiffnessMat_Matrix(Cur.AFree, Cur.ElementsL, Cur.ElementsA, Cur.ElementsE)

    def ConnectivityMatrix(Self, NodesCount, ElementsCount, ElementsEndNodes):
        """
        :return: the connectivity matrix C of shape (ElementsCount, NodesCount). C contains the same info than ElementsEndNodes but presented under a matrix form.
        """

        #Calculation according to references
        # Vassart, Motro, 1999, Multiparametered Formfinding Method: Application to Tensegrity Systems
        # Sheck, 1974, The force density method for formfinding and computation of networks

        C = np.zeros((ElementsCount, NodesCount), dtype=int)  # connectivity matrix C
        for line_ind, line_extremities in enumerate(ElementsEndNodes):
            n0 = line_extremities[0]
            n1 = line_extremities[1]
            C[line_ind, n0] = 1
            C[line_ind, n1] = -1

        return -C  #- signe because it makes more sense to do n1-n0 (than n0-n1) when computing a cosinus (X1-X0)/L01. But this actually do not change the equilibrum matrix.
        # print(C)

    def StackedConnectivityMatrix(Self,C):
        """
        Stack the connectivity matrix such that each row (=1element) is arranged according to the DOF [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        :param C: [/] - shape (ElementsCount, NodesCount) - the connectivity matrix
        :return: Cxyz: [/] - shape (ElementsCount, 3*NodesCount) - the connectivity matrix stacked 3 times
        """
        #1) Check inputs
        ElementsCount = Self.ElementsCount
        NodesCount = Self.NodesCount
        assert C.shape == (ElementsCount, NodesCount), "Please check the connectivity matrix C shape"

        #2) Stack the degrees of freedoms
        Cxyz = np.zeros((ElementsCount, 3 * NodesCount))

        for i in range(NodesCount):
            Cxyz[:, 3 * i] = C[:,i]
            Cxyz[:, 3 * i + 1] = C[:,i]
            Cxyz[:, 3 * i + 2] = C[:,i]

        return Cxyz




    # endregion

    # region Private Methods : Linear Solver based on displacement methods

    def Core_LinearSolve_Displ_Method(S0):

        S0.C = S0.ConnectivityMatrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (S0.ElementsLFree, S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.NodesCoord, S0.C)

        perturb = 1e-6  # [m], à appliquer si matrice singulière uniquement

        d = np.zeros((3*S0.NodesCount,1))
        AxialForces = np.zeros((S0.ElementsCount,1))
        Reactions = np.zeros((S0.FixationsCount,1))

        try:
            (d, AxialForces, Reactions) = S0.LinearSolve_Displ_Method(S0.NodesCoord, S0.AxialForces_Already_Applied, S0.Loads_To_Apply)

        except np.linalg.linalg.LinAlgError:
            # print("la matrice est singulière")
            NodesCoord_perturbed = S0.Perturbation(S0.NodesCoord, S0.IsDOFfree, perturb)
            (d, AxialForces, Reactions) = S0.LinearSolve_Displ_Method(NodesCoord_perturbed, S0.AxialForces_Already_Applied,S0.Loads_To_Apply)
        finally:
            S0.Displacements_Results = d
            S0.AxialForces_Results = AxialForces
            S0.Reactions_Results = Reactions

    def LinearSolve_Displ_Method(cur, NodesCoord, AxialForces_Already_Applied, Loads_To_Apply):

        #1) Input
        n = cur.NodesCount
        c = cur.FixationsCount

        Elements_L0 = cur.ElementsLFree #  = Cur.ElementsLFree : Initial Lengths
        Elements_A = cur.ElementsA
        Elements_E = cur.ElementsE
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
        Elements_ExtremitiesIndex=cur.ElementsEndNodes

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
        Elements_ExtremitiesIndex = cur.ElementsEndNodes
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

        S0.C = S0.ConnectivityMatrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (S0.ElementsLFree, S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.NodesCoord, S0.C)

        (Stages,StagesLoad,StagesDispl,StagesN,StagesR) = S0.NonLinearSolve_Displ_Method(S0.n_steps, S0.NodesCoord, S0.AxialForces_Already_Applied, S0.Loads_To_Apply)
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
                (v, N, R) = cur.LinearSolve_Displ_Method(cur.NodesCoord, cur.AxialForces_Already_Applied, cur.Loads_To_Apply)
            except np.linalg.LinAlgError:
                # print("la matrice est singulière")
                NodesCoord_perturbed = cur.Perturbation(cur.NodesCoord, cur.IsDOFfree, perturb)
                (v, N, R) = cur.LinearSolve_Displ_Method(NodesCoord_perturbed,cur.AxialForces_Already_Applied,cur.Loads_To_Apply)
            finally:
                cur.Displacements_Results = v #Linear results
                cur.AxialForces_Results = N
                cur.Reactions_Results = R

                if k==0: # Initial Structure = current at first step
                    S0.Elements_L = cur.ElementsL
                    S0.Elements_Cos = cur.ElementsCos
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
                (v, N, R) = cur.LinearSolve_Displ_Method(cur.NodesCoord, cur.AxialForces_Already_Applied, cur.Loads_To_Apply)
            except np.linalg.LinAlgError:
                # print("la matrice est singulière")
                NodesCoord_perturbed = cur.Perturbation(cur.NodesCoord, cur.IsDOFfree, perturb)
                (v, N, R) = cur.LinearSolve_Displ_Method(NodesCoord_perturbed,cur.AxialForces_Already_Applied,cur.Loads_To_Apply)
            finally:
                cur.Displacements_Results = v #Linear results
                cur.AxialForces_Results = N
                cur.Reactions_Results = R

                if k==0: # Initial Structure = current at first step
                    S0.Elements_L = cur.ElementsL
                    S0.Elements_Cos = cur.ElementsCos
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
        S0.C = S0.ConnectivityMatrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (S0.ElementsLFree, S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.NodesCoord, S0.C)
        (S0.A, S0.AFree, S0.AFixed) = S0.Compute_Equilibrium_Matrix(S0.Elements_Cos0, S0.C, S0.IsDOFfree)

        d0 = np.zeros((3*S0.NodesCount,1)) #initial displacements
        t0 = S0.AxialForces_Already_Applied #initial forces at first step
        p0 = S0.Loads_Already_Applied[S0.IsDOFfree] #initial load already applied on the structure

        p_ToApply = S0.Loads_To_Apply[S0.IsDOFfree] #external point loads to apply on the free dofs
        e_ToApply = S0.Elongations_To_Apply  #elongations to apply

        dp_free = p_ToApply + p0 - S0.AFree @ t0 #unbalanced loads. AFree @ t0 should be equal to p0 if the initial structure is in equilibrium.

        ## 0) Compute the SVD of At
        SVD = S0.SVD_Equilibrium_Matrix(S0.AFree)

        ## 1) Solve Equilibrium A @ dt = dp   to find the increment of tensions dt due to unbalanced load and external elongations
        S0.F = S0.Flexibility_Matrix(S0.ElementsE, S0.ElementsA, S0.ElementsLFree)
        (dt, de) = S0.Equilibrium_Analysis(SVD,S0.F,dp_free,e_ToApply)

        ## 2) Solve Compatibility Bt @ dd = de to find the increment of displacements dd due to unbalanced loads and external elongations
        G = S0.Geometric_Loads_Matrix(SVD,t0)
        dd_free = S0.Compatibility_Analysis(SVD,G,de)
        dd = np.zeros((3 * S0.NodesCount, 1))
        dd[S0.IsDOFfree] = dd_free

        S0.AxialForces_Results = dt
        S0.Displacements_Results = dd




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
            Elements_Cos_Displ = S0.Compute_Elements_Reorientation(Um_i, S0.C, S0.ElementsLFree)
            (A_nl, A_nl_free, A_nl_fixed) = S0.Compute_NL_Equilibrium_Matrix(Elements_Cos_Displ, S0.C, S0.IsDOFfree)
            G_i = A_nl_free @ t0
            G[:,i] = G_i

        # Cur.Kg_mod = Cur.Um_t @ G
        # Cur.Kg = G @ Cur.Um_t
        # print(G)
        return G

    def Compute_Elements_Reorientation(S0,Displacements,C,Elements_L0):
        """
        Calculates the Lines properties (Lengths, CosDir) based on the given NodesCoord and Connectivity Matrix C, and store it in Cur
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
        S0.C = S0.ConnectivityMatrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (S0.ElementsLFree, S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.NodesCoord, S0.C)
        (S0.A, S0.AFree, S0.AFixed) = S0.Compute_Equilibrium_Matrix(S0.Elements_Cos0, S0.C, S0.IsDOFfree)
        S0.F = S0.Flexibility_Matrix(S0.ElementsE, S0.ElementsA, S0.ElementsLFree)

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
        # IncrR = np.zeros((Cur.FixationsCount,1)) #Incr of Reaction at this step.

        # Stage 0
        d = d0.copy() #list of Displacement at all stages k.
        t = t0.copy() #list of AxialForces at all stages k.
        # StagesR = IncrR.copy() #list of Reactions at all stages.

        while (k <= kmax and err>= tol):

            # A new initial structure is considered at each step. A Linear Solve method is applied on it.
            Prev_d = d[:, k-1].reshape((-1, 1))
            Prev_t = t[:,k-1].reshape((-1,1))

            Elements_Cos_Displ = S0.Compute_Elements_Reorientation(Prev_d, S0.C, S0.ElementsLFree)
            (A_nl, A_nl_free, A_nl_fixed) = S0.Compute_NL_Equilibrium_Matrix(Elements_Cos_Displ, S0.C, S0.IsDOFfree)
            A_t = S0.A+A_nl
            A_t_free = S0.AFree + A_nl_free

            dp_free = p_ToApply + p0 - A_t_free @ Prev_t  # unbalanced loads. AFree @ t0 should be equal to p0 if the initial structure is in equilibrium.

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




