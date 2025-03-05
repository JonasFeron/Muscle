import numpy as np
import scipy.linalg as lin

from data import SharedData


#All kinds of objects are defined here in a single file in order to avoid the user to unblock manually too many files
#at the installation stage. I know it is a bit messy, but it is for the sake of the user best experience.

class ResultsSVD():
    """
    This class stores the results into a ResultsSVD object of the Singular Value Decomposition of the Equilibrium Matrix of the structure in the current state.
    Ref: Pellegrino, 1993, Structural computations with the singular value decomposition of the equilibrium matrix
    """

    def __init__(SVD):
        """
        Initialize an empty ResultsSVD object ready to store the results
        """
        NodesCount = 0
        ElementsCount = 0
        FixationsCount = 0
        DOFfreeCount = 3*NodesCount - FixationsCount

        SVD.S = np.zeros((DOFfreeCount,)) #eigen values of AFree
        SVD.r = 0  # number of non null eigen value. rank of AFree
        SVD.Sr = np.zeros((SVD.r,)) #non null eigen values of AFree

        SVD.s = ElementsCount - SVD.r #degree of static indeterminacy = nbr of self-stress modes
        SVD.Vr_row = np.zeros((SVD.r, ElementsCount)) # r row eigen vectors. Interpretation: Bar tensions in equilibrium with the Diag(Struct)* Loads of Ur OR Bar elongations compatible with Diag(1/Struct) * Extensional displacements of Ur
        SVD.Vs_row = np.zeros((SVD.s, ElementsCount)) # s row eigen vectors. Interpretation: DR-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
        SVD.SS = np.zeros((SVD.s, ElementsCount))  # s row eigen vectors. =Vs_row but rescaled to have the biggest force = -1 (compression) in each vector. Interpretation: rescaled DR-stress modes

        SVD.m = DOFfreeCount - SVD.r #degree of kinematic indeterminacy = nbr of mechanisms
        SVD.Ur_row = np.zeros((SVD.r, 3 * NodesCount)) #same as free but considering 0 reaction/displacement at the support.
        SVD.Ur_free_row = np.zeros((SVD.r, DOFfreeCount)) # r row eigenvectors. Interpretation: Loads which can be equilibrated in the current struct OR Extensional displacements
        SVD.Um_row = np.zeros((SVD.m, 3 * NodesCount)) #same as free but considering 0 reaction/displacement at the support.
        SVD.Um_free_row = np.zeros((SVD.m, DOFfreeCount)) # m row eigenvectors. Interpretation: Loads which can not be equilibrated in the current struct OR Inextensional displacements (sol of B@d = 0)

        #IF FLEXIBILITY of the STRUCTURE has been defined
        SVD.Ks = np.zeros((SVD.s, SVD.s)) # [N/m] - stiffness matrix of the self-stress modes
        SVD.Sa = np.zeros((SVD.s, ElementsCount)) # [N/m] Sensitivity of the prestress level to a given elongation
        SVD.Sd = np.zeros((3 * NodesCount, ElementsCount)) # [m/m] Sensitivity of the displacements to a given elongation


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

    def SVDEquilibriumMatrix(SVD, Struct, AFree, ZeroTol=1e-3):
        """
        Compute the Singular Value Decomposition of the Equilibrium Matrix of the structure
        :param ZeroTol:
        :param Struct: The structure object
        :param AFree: The Equilibrium Matrix. shape (DOFfreeCount, ElementsCount)
        :return: The resulting (eigen) vectors of the Equilibrium Matrix decomposition
        """
        # 1) retrieve and check inputs
        ElementsCount = Struct.ElementsCount
        NodesCount = Struct.NodesCount
        DOFfreeCount = Struct.DOFfreeCount
        IsDOFfree = Struct.IsDOFfree

        assert AFree.shape == (DOFfreeCount, ElementsCount), "Please check the equilibrium matrix (AFree) shape"
        assert np.abs(AFree).sum() != 0, "Please check that the equilibrium matrix (AFree) has been computed"

        #Note the following notation:
        #Free if the dimension(s) of the vector/matrix correspond to the number of free degrees of freedom (DOFfreeCount)
        #Row if the eigen vectors are horizontal
        #Col if the eigen vectors are vertical
        #We only store the Row eigenvectors. Please transpose the matrice to obtain the Col eigenvectors.

        # 2) calculate the eigenvalues and vectors
        U_free_col, S, V_row = np.linalg.svd(AFree)  # Struct contains the eigen values of AFree in decreasing order. U_col is a matrix (nbr free DOF,nbr free DOF) containing the column eigen vectors. V_row is a matrix (nbr lines,nbr lines) containing the row eigen vectors.

        Lambda_1 = S.max()
        Tol = Lambda_1 * ZeroTol  # Tol is the limit below which an eigen value is considered as null.
        Sr = S[S >= Tol]  # non null eigen values
        r = Sr.size  #number of non null eigen value. rank of AFree
        m = DOFfreeCount - r  #degree of kinematic indeterminacy = nbr of mechanisms
        s = ElementsCount - r  #degree of static indeterminacy = nbr of self-stress modes

        # 3a) Interprete the eigenVectors in the elements space
        Vr_row = V_row[:r,:]  # r row eigen vectors (,nbr lines). Interpretation: Bar tensions in equilibrium with the Diag(Struct)* Loads of Ur OR Bar elongations compatible with Diag(1/Struct) * Extensional displacements of Ur
        Vs_row = np.zeros((s, ElementsCount)) # s row eigen vectors. Interpretation: DR-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
        SS = np.zeros((s, ElementsCount)) # s row eigen vectors. =Vs_row but rescaled to have the biggest force = -1 (compression) in each vector. Interpretation: rescaled DR-stress modes

        if s != 0: #rescale the eigen vectors Vs_row such that the highest value = -1 (compression) and store the results in the DR-Stress mode matrix SS.
            Vs_row = V_row[-s:,:]  # s Vecteurs (lignes) propres (associés aux VaP nulles) de longueur ElementsCount. Interprétations : DR-stress modes (sol of A@t=0) (=Bar tensions in equilibrium without external loads) OR incompatible Bar elongations (=bar elongations which can't be obtained in this geometry)
            SS = SVD.SortSelfStressModes(Struct,Vs_row)

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

    def SortSelfStressModes(SVD, Struct, Vs_row):
        """

        :param Struct:
        :param Vs_row: [/] - shape (s,ElementsCount) - the s row eigen vectors of the equilibrium matrix
        :return:
        """

        #ref
        # L. R. Sanchez Sandoval, “Contribution à l’étude du dimensionnement optimal des systèmes de tenségrité,” Université Montpellier II, 2005. p 49
        # R. Sánchez, B. Maurin, M. N. Kazi-Aoual, and R. Motro, “Selfstress States Identification and Localization in Modular Tensegrity Grids:,” Int. J. Sp. Struct., vol. 22, no. 4, pp. 215–224, Nov. 2007.

        assert Struct.Initial.ElementsL.size > 0
        (s, b) = Vs_row.shape
        L = np.diag(Struct.Initial.ElementsL)
        Linv = np.diag(1/Struct.Initial.ElementsL)
        qs_row = Vs_row @ Linv # [1/m] - shape (s,ElementsCount) - force densities associated to each self-stress mode. One row = one mode. One column = one element.
        qs_row_sorted1 = SVD.RecursiveSelfStressReduction(Struct, qs_row)
        qs_row_sorted2 = SVD.SortReducedSSModes(qs_row_sorted1)
        Vs_row_sorted = qs_row_sorted2 @ L

        # unitize the max value of each mode
        SS = np.zeros((s, b))
        ZeroTol = 1e-6
        for i in range(s):
            mode = Vs_row_sorted[i]
            CompressionMax = mode.min()
            TensionMax = mode.max()
            bool = -CompressionMax > TensionMax  # true if |compression max| > tension max
            max = np.where(bool, CompressionMax, TensionMax)
            SS[i] = -mode/max # self-stress modes Matrix. we made sure the max value is always equal to -1 in compression whatever the mode

            # if the mode activates some elements only in compression, i.e. no element is in tension, then reverse the sign
            # -> then the mode activates some elements only in tension but there are no element in compression
            if SS[i].max()<= +ZeroTol: #if the highest force is smaller than or equal to 0, then the mode activates only element in compression
                SS[i] *= -1 #then reverse the sign

        return SS




    def RecursiveSelfStressReduction(SVD, Struct, modesBrut):

        # Part 1 : sort the modes (=row) per number of elements involved in the modes.
        # The modes with the less elements (the more localized modes) are placed first.
        # The modes with the more elements (the more generalized modes) are placed last.
        (s, b) = modesBrut.shape
        if s<= 1 :
            return modesBrut

        ZeroTol = 1e-6
        numberElementsPerMode = np.sum(np.where(~np.isclose(modesBrut, np.zeros((s, b)), atol=ZeroTol), True, False), axis=1)
        # numberElementsperMode = np.array([1,0])

        ind = np.argsort(numberElementsPerMode)  # sort from the smallest to the biggest
        modesSorted = modesBrut[ind]
        numberElementsPerMode_sorted = numberElementsPerMode[ind]

        # Part 2: Seek to perform a reduction Lj -> Lj - Li * Lj[k]/Li[k]
        performReduction = False
        mode = modesSorted  # simplify the word. one mode = one row L
        # i = 0  # the row of the mode with the less elements
        # j = 1  # the row of the mode with more elements where we seek to reduce the number of elements thanks to row i.
        # k  # the pivot (column number) where the reduction may be performed
        for j in range(s-1, 0,-1):
            for i in range(0, j):
                for k in range(b-1, -1,-1):
                    if (np.isclose(mode[i][k],0,atol=ZeroTol) or np.isclose(mode[j][k],0,atol=ZeroTol)): #if mode[i][k]==0 or mode[j][k]==0
                        continue  # go to k++
                    # if mode[i][k]!=0 AND mode[j][k]!=0 then DO

                    # test if the reduction will reduce the number of elements in the mode j
                    modeI = mode[i][:].copy()
                    modeJ = mode[j][:].copy()
                    modeJ -= modeI * (modeJ[k] / modeI[k])
                    modeJ = np.where(np.isclose(modeJ, np.zeros((b,)), atol=ZeroTol), 0, modeJ)
                    numberElementsInModeJ = np.sum(np.where(modeJ!=0,1,0))
                    # test if the numberElementsInModeJ has reduced
                    performReduction = numberElementsInModeJ < numberElementsPerMode_sorted[j]

                    if numberElementsInModeJ == numberElementsPerMode_sorted[j]: #if the reduction keeps the same number of elements
                        # then perform the reduction if it allows to put cables in tension or struts in compression

                        numberElementsConformBefore = np.sum(np.sign(mode[j])==Struct.ElementsType)
                        numberElementsConformAfter = np.sum(np.sign(modeJ) == Struct.ElementsType)
                        performReduction = numberElementsConformAfter > numberElementsConformBefore



                    if performReduction:  # truly perform the reduction if the numberElementsInModeJ has reduced
                        mode[j][:] -= mode[i][:] * (mode[j][k] / mode[i][k])
                        mode[j] = np.where(np.isclose(mode[j], np.zeros((b,)), atol=ZeroTol), 0, mode[j])

                        #unitize the pivot
                        CompressionMax = mode[j].min()
                        TensionMax = mode[j].max()
                        bool = -CompressionMax > TensionMax  # true if |compression max| > tension max
                        max = np.where(bool, CompressionMax, TensionMax)
                        mode[j] = -mode[j] / max  # self-stress modes Matrix. we made sure the max value is always equal to -1 in compression whatever the mode

                        #check that the sign of the force respects the type of the elements
                        numberElementsConform = np.sum(np.sign(mode[j])==Struct.ElementsType)
                        numberElementsAntiConform = np.sum(np.sign(-mode[j]) == Struct.ElementsType)

                        if numberElementsAntiConform > numberElementsConform:
                            mode[j] = -mode[j]
                        # restart at part 1.
                        break

                    else:  # do not perform the reduction, try with the next pivot
                        continue

                if performReduction:
                    break
            if performReduction:
                break

        if performReduction:
            mode = SVD.RecursiveSelfStressReduction(Struct, mode)

        return mode

    def SortReducedSSModes(SVD, reducedModes):
        """
        Sort the reduced modes (coming out of the RecursiveSelfStressReduction method) such that the first self-stress mode correspond to the first module
        :param reducedModes:
        :return: sortedModes
        """
        (s, b) = reducedModes.shape
        if s <= 1:
            return reducedModes

        ZeroTol = 1e-6
        numberElementsPerMode = np.sum(np.where(~np.isclose(reducedModes, np.zeros((s, b)), atol=ZeroTol), True, False),axis=1)
        # 1) The reducedmodes are sorted from the smallest numberElementsPerMode to the biggest.
        #    But if two or more modes have the same numberElementsPerMode, they are not sorted.
        #    So, find which modes have the same numberElementsPerMode, and sort them.

        # 2) find which modes have the same numberElementsPerMode
        #    for instance, if 1 self-stress mode activates 2 elements and 3 self-stress modes activate 6 elements
        #    then  numberElementsPerMode = [2, 6, 6, 6]
        uniqueSet = np.unique(numberElementsPerMode) # and  uniqueSet = [2, 6]
        sortedModes = np.zeros((s, b))
        for numberElements in uniqueSet:
            group = np.where(numberElementsPerMode == numberElements)
            sortedModes[group] = SVD.SortGroupOfModes(reducedModes[group])
        return sortedModes

    def SortGroupOfModes(SVD, groupOfModes):
        """
        Sort each group of self-stress modes. Each mode of the group activates the same number of elements.
        :param groupOfModes:
        :return: sortedModes: the first mode correspond to the first module.
        """
        (sub_s, b) = groupOfModes.shape
        ZeroTol = 1e-6
        if sub_s <= 1:
            return groupOfModes

        #1) find the position of the first element being activated for each mode
        IndexFirstOccurence = np.zeros((sub_s,)) #the index of the first element being activated
        for groupI in range(sub_s):
            modeI = groupOfModes[groupI]
            IndexFirstOccurence[groupI] = np.argwhere(~np.isclose(modeI, np.zeros((b,)), atol=ZeroTol))[0][0]

        sort = np.argsort(IndexFirstOccurence) #the first mode of the group correspond to the first module
        sortedGroupOfModes = groupOfModes[sort]
        return sortedGroupOfModes


    def SensitivityMatrix(SVD, Struct):
        """
        Compute Sensitivity Matrices in the Initial state according to [ref] Xue, Y. et al. (2021) “Comparison of different sensitivity matrices relating element elongations to structural response of pin-jointed structures,”

        :param Struct:
        :return:
        """

        L = Struct.Initial.ElementsL
        Struct.Initial.Flex = Struct.Flexibility(Struct.Initial.ElementsE, Struct.Initial.ElementsA, L)

        SS = SVD.SS.T # SVD.SS is a row matrix to be transposed
        s = SVD.s

        F = np.diag(Struct.Initial.Flex)
        Ke = np.diag(1 / Struct.Initial.Flex)


        AFree = Struct.Initial.AFree # [/] - (nbr dof, nbr lines) - the equilibrium matrix
        BFree = AFree.T  # [/] - (nbr lines,nbr dof) - the compatibility matrix
        B = Struct.Initial.A.T  # [/] - (nbr lines, 3 * nbr nodes) - the compatibility matrix


        # According to [1] and [2]
        SFS = SS.T @ F @ SS  # This is the flexibility of the self-stress modes! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        Ks = np.linalg.inv(SFS) # Stiffness of the self-stress modes
        Sa = -Ks @ SS.T  # Sensitivity of the prestress level to a given elongation
        St1 = SS @ Sa  # Sensitivity of the tensions to a given elongation
        Se1 = F @ St1  # Sensitivity of the elastic elongations to a given imposed elongation

        B__ = np.linalg.pinv(BFree)  # the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        Sd1 = B__ @ (Se1 + np.eye(Struct.ElementsCount))  # Sensitivity of the displacements to a given imposed elongation, assuming the elongation do not activate the mechanism.

        Sd = np.zeros((3 * Struct.NodesCount,Struct.ElementsCount))
        Sd[Struct.IsDOFfree,:] = Sd1


        # # According to method2 of [ref]
        # Kmat = AFree @ Ke @ BFree
        # Kmat__ = np.linalg.pinv(Kmat)
        # Sd2 = Kmat__ @ AFree @ Ke  # equivalent to Sd1
        # St2 = Ke @ BFree @ Sd2 - Ke  # equivalent to St1


        # # According to method2 of [ref]
        # t0 = Struct.Initial.Tension  # prestress forces [N] # assumption no self-weight
        # q = Struct.Initial.ForceDensities(t0, L)  #
        # kgLocList = Struct.Initial.GeometricLocalStiffnessList(Struct, q)
        # Kgeo = Struct.LocalToGlobalStiffnessMatrix(kgLocList)
        # KgeoFree = Kgeo[Struct.IsDOFfree].T[Struct.IsDOFfree].T
        #
        # Ktan__ = np.linalg.inv(Kmat + KgeoFree)
        # Sd3 = Ktan__ @ AFree @ Ke
        # St3 = Ke @ BFree @ Sd3 - Ke

        SVD.Ks = Ks
        SVD.Sa = Sa
        SVD.Sd = Sd
        #return (Ks, Sa, Sd1)

    # def ConformSelfStressState(SVD, Struct, Vs_row):
    #     # linear programming method to find a conform self-stress state i.e. which respect tension in cables
    #     # solve
    #     # Minimize nothing
    #     # variables : a1 ... a_s     # a : the vector of the prestress levels associated to each mode
    #     # subject to constrains:
    #     # 1) tension in cable i = SS1 * a1 + SS2 * a2 + ... + SS_s * a_s >= 0. the total tension in the cable i comes from the participation of different self-stress modes SS
    #     # 2) a1 + a2 + ... + a_s = 1    #to make sure the solution is not trivial (all a_i = 0)
    #
    #     type = Struct.ElementsType
    #     Iscable = np.where(type > 0, True, False)
    #     number_cables = np.sum(Iscable)
    #     # constrain 1) to ensure the cables are in tensions
    #     Aub = SS[Iscable]  # impose constrain on all the cables :  SS1 * a1 + SS2 * a2 + ... + SS_s * a_s >= 0
    #     Aub = Aub * -1  # impose constrain on all the cables :  -(SS1 * a1 + SS2 * a2 + ... + SS_s * a_s) <= 0
    #     smaller_0 = np.zeros((number_cables,))
    #
    #     # constrain 2) to make sure the solution is not trivial
    #     c = np.ones((s, 1))  # c.T @ a = a1 + a2 + ... + a_s   # = 1
    #     equal1 = np.ones((1,))
    #
    #     # stack all the constrains
    #     x0 = np.zeros((s,))
    #     x0[0] = 1.0
    #     options = {'maxiter': 5000, 'disp': True, 'presolve': True, 'tol': 1e-3, 'autoscale': False, 'rr': True,
    #                'maxupdate': 10, 'mast': False, 'pivot': 'bland'}
    #
    #     res = opt.linprog(-np.ones((s, 1)).T, A_ub=Aub, b_ub=smaller_0, A_eq=c.T, b_eq=equal1, method='revised simplex',
    #                       x0=x0, options=options)
    #




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

    def Copy(Cur):
        """
        Copy the current state
        :return: Copy: A new State object with the same properties than the current state
        """
        Copy = State() #create a new state of the Structure Struct

        Copy.NodesCoord = Cur.NodesCoord.copy()
        Copy.Loads = Cur.Loads.copy()
        Copy.Tension = Cur.Tension.copy()
        Copy.Reactions = Cur.Reactions.copy()

        Copy.ElementsL = Cur.ElementsL.copy()
        Copy.ElementsLFree = Cur.ElementsLFree.copy()
        Copy.ElementsCos = Cur.ElementsCos.copy()
        Copy.ElementsA = Cur.ElementsA.copy()
        Copy.ElementsE = Cur.ElementsE.copy()
        Copy.A = Cur.A.copy()
        Copy.AFree = Cur.AFree.copy()
        Copy.AFixed = Cur.AFixed.copy()
        Copy.SVD = ResultsSVD()  # An empty results SVD object

        Copy.Residual = Cur.Residual.copy()
        Copy.IsInEquilibrium = False
        Copy.Flex = Cur.Flex.copy()
        Copy.Kmat = Cur.Kmat.copy()
        Copy.Kgeo = Cur.Kgeo.copy()
        Copy.DRState = Cur.DRState.Copy()
        return Copy

    def ComputeState(Cur, Struct, ComputeResidual=True, ComputeStiffness=True):
        """
        Assemble the equilibrim Matrix and the material stiffness matrix. N.B. Do not perfom the SVD -> do it separately
        :param Struct:
        :param ComputeResidual:
        :param ComputeStiffness:
        :return: All computation Results are stored in the Current State.
        """
        assert int(ComputeStiffness) <= int(ComputeResidual), "The stiffness cannot be computed if the residual (and the tension) have not been computed"
        assert Cur.NodesCoord.shape == (3*Struct.NodesCount,), "Please check the shape of NodesCoord"
        assert Cur.ElementsLFree.shape == (Struct.ElementsCount,), "Please check the shape of ElementsLFree"

        (Cur.ElementsL, Cur.ElementsCos) = Cur.ElementsLengthsAndCos(Struct, Cur.NodesCoord)
        (Cur.A, Cur.AFree, Cur.AFixed) = Cur.EquilibriumMatrix(Struct, Cur.ElementsCos)

        if ComputeResidual:
            ElementsE = Struct.ElementsE  # will be asserted in a deeper method
            ElementsA = Struct.ElementsA  # will be asserted in a deeper method

            (Cur.Tension, Cur.Flex) = Cur.TensionForces(Struct, Cur.ElementsL, Cur.ElementsLFree, ElementsE, ElementsA)  # Flex = LFree/EA. T=(Lcur-Lfree)/Flex. Flex can be infinity and T=0 if slack cables
            Cur.Residual = Cur.UnbalancedLoads(Struct, Cur.AFree, Cur.Loads, Cur.Tension)
            Cur.IsInEquilibrium = Cur.CheckEquilibrium(Struct, Cur.Residual, Struct.Residual0Threshold)

            if ComputeStiffness:
                Cur.Kmat = Cur.MaterialStiffnessMatrix(Struct, Cur.A, Cur.Flex)  # note that material stiffness associated to slack cables = 0
                Cur.Kgeo = Cur.GeometricStiffnessMatrix(Struct, Cur.Tension, Cur.ElementsL)


    def ComputeSVD(Cur, Struct, AFree):
        """
        :param Struct: The StructureObject
        :param AFree: The Equilibrium Matrix with shape (DOFfreeCount, ElementsCount)
        :return: the ResultsSVD object in the current state is filled with the results of the singular value decomposition of AFree
        """
        Cur.SVD.SVDEquilibriumMatrix(Struct, AFree)  # Compute and store the results of the singular value decompositon of AFree in the current state
        return Cur.SVD

    def TensionForces(Cur, Struct, ElementsLCur, ElementsLFree, ElementsE, ElementsA):
        """

        :param Struct: The StructureObject in the current state
        :param ElementsLCur: [m] - shape (ElementsCount,) - Current lengths of the elements.
        :param ElementsLFree: [m] - shape (ElementsCount,) - Free lengths of the elements.
        :param ElementsE: [MPa] - shape (ElementsCount,2) - Young modules [EinComp, EinTens] of the elements in compression and in tension.
        :param ElementsA: [mm²] - shape (ElementsCount,2) - Areas [AinComp, AinTens] of the elements in compression and in tension.
        :return: T: [N] - shape (ElementsCount,) - The tension forces in each elements.
        """

        # TensionInit = np.zeros((0,))
        # assert TensionInit.size == ElementsCount or TensionInit.size == 0 , "Please check the shape of TensionInit"

        # 1) Check the inputs

        ElementsCount = Struct.ElementsCount
        assert ElementsLCur.shape == (ElementsCount,), "Please check the shape of ElementsLCur"
        assert ElementsLFree.shape == (ElementsCount,), "Please check the shape of ElementsL0"

        # 2) Check the state of the elements (in compression or in tension) and find their associated stiffness

        # For each elements, there is one E value in case of compression and another value in case of tension. Idem for A
        # For instance, the Young modulus of a cable could be 0 in compression and 100e3 MPa in tension.
        # In this case, the cable vanish from stiffness matrix if it slacks
        DeltaL = ElementsLCur - ElementsLFree
        Cur.ElementsE = Struct.ElementsInTensionOrCompression(DeltaL,
                                                  ElementsE)  # the Young modulus of the elements in the current state (depending if compression or tension)
        Cur.ElementsA = Struct.ElementsInTensionOrCompression(DeltaL,
                                                  ElementsA)  # the Area of the elements in the current state (depending if compression or tension)

        # 3) Compute the elements flexibility L/EA and stiffness EA/L

        Flex = Struct.Flexibility(Cur.ElementsE, Cur.ElementsA, ElementsLFree)  # shape (ElementsCount,). Important to note that the Free lengths are considered in the flexibility
        Kbsc = 1 / Flex  # shape (ElementsCount,). basic material stiffness vector of each individual element

        # 4) Compute the tension

        T = Kbsc * DeltaL  # shape (ElementsCount,)  T = EA/Lfree * (Lcur - Lfree)
        return (T, Flex)




#region Dynamic Relaxation

#endregion Dynamic Relaxation

class StructureObj():

    # region Constructors
    def __init__(Self):
        """
        Initialize an empty structure. A structure object contains all data which do not vary in time, or in other words, which do not depends on the current state of the structure.
        """
        Self.NodesCount = 0
        Self.ElementsCount = 0
        Self.FixationsCount = 0
        Self.DOFfreeCount = 3 * Self.NodesCount - Self.FixationsCount


        ##### Structure inputs #####
        Self.Initial = State()  # the Initial State of the structure which may already be loaded or prestressed from a previous calculation.
        Self.Start = None  # the Start State of the structure = the Initial State + New LoadsToApply and LengtheningsToApply. we must seek for a new equilibrium from the Start state and via intermediate states
        Self.Final = None  # the Final or Deformed State of the structure in equilibrium with all loads and all elongations.
        #Self.NodesCoord = np.zeros((3 * DR.NodesCount,)) #The NodesCoord depend on the Structure State.
        Self.ElementsEndNodes = np.zeros((Self.ElementsCount, 2), dtype=int)
        Self.ElementsA = np.zeros((Self.ElementsCount,2)) # Area [mm²] - [AinCompression, AinTension] for each element
        Self.ElementsE = np.zeros((Self.ElementsCount,2)) # Young Modulus [MPa] - [EinCompression, EinTension] for each element
        Self.ElementsType = np.zeros((Self.ElementsCount,)) # [/] - Type = -1 if the element mainly behave in compression such as struts, Type = 1 if the element mainly behave in tension such as cables
        Self.IsDOFfree = np.zeros((3 * Self.NodesCount,), dtype=bool) #the supports conditions

        Self.LoadsToApply = np.zeros((3 * Self.NodesCount,)) #The additionnal external loads to apply on the inital state of the structure
        Self.LengtheningsToApply = np.zeros((Self.ElementsCount,)) #The additionnal lengthenings to impose on the elements free lengths of the structure

        ##### Structure Calculated #####

        Self.C = np.zeros((Self.ElementsCount, Self.NodesCount), dtype=int) #matrice de connectivité C # (nbr lines, nbr nodes)

        ##### Solve informations #####
        Self.Residual0Threshold = 0.0001 # the Zero threshold = tolerance below which the (norm of the) residual forces are considered equal to 0, in other words, the structure is in equilibrium.

        Self.DR = DRMethod()
        Self.n_steps = 1

        #Part Dynamics
        Self.DynMasses = np.zeros((Self.NodesCount,))  # Mass [kg] used for the dynamics computation  - scalar
        Self.MassElement = np.zeros((Self.ElementsCount,))
        Self.freq = np.zeros((Self.DOFfreeCount,))
        Self.mode = np.zeros((Self.DOFfreeCount,Self.DOFfreeCount))
        Self.TotMode = np.zeros((len(Self.IsDOFfree),Self.DOFfreeCount))
        Self.MaxFreqWanted = 0
    # endregion


    # region Private Methods : Assemble a structure
    def StartState(Self,LoadsToApply,LengtheningsToApply):
        """

        :param LoadsToApply:
        :param LengtheningsToApply:
        :return: Start
        """
        assert LoadsToApply.shape== (3*Self.NodesCount,),"Please check the shape of LoadsToApply"
        assert LengtheningsToApply.shape== (Self.ElementsCount,),"Please check the shape of LengtheningsToApply"

        Init = Self.Initial
        Start = Init.Copy()
        Start.Loads += LoadsToApply
        Start.ElementsLFree += LengtheningsToApply
        return Start



    # endregion


    # endregion

    # region Public Methods : Main
    def MainAssemble(Self, Data):
        Self.InitialData(Data.NodesCoord, Data.ElementsEndNodes, Data.IsDOFfree, Data.ElementsType, Data.ElementsA, Data.ElementsE,
                         Data.ElementsLFreeInit, Data.LoadsInit, Data.TensionInit, Data.ReactionsInit, Data.LoadsToApply, Data.LengtheningsToApply, Data.Residual0Threshold)
        Self.Initial.ComputeState(Self,False,False)
        Self.Initial.SVD.SVDEquilibriumMatrix(Self, Self.Initial.AFree, Self.Residual0Threshold)
        Self.Initial.SVD.SensitivityMatrix(Self)


    def test_MainAssemble(Self, NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                                   ElementsLFreeInit=-1, LoadsInit=np.zeros((0,)),
                                   TensionInit=np.zeros((0,)), ReactionsInit=np.zeros((0,)),
                                   LoadsToApply=np.zeros((0,)), LengtheningsToApply=np.zeros((0,)),
                                   Residual0Threshold=0.001):

        Self.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                         ElementsLFreeInit, LoadsInit, TensionInit, ReactionsInit,
                         LoadsToApply, LengtheningsToApply, Residual0Threshold)
        Self.Initial.ComputeState(Self,False,False)
        Self.Initial.SVD.SVDEquilibriumMatrix(Self, Self.Initial.AFree, Self.Residual0Threshold)
        Self.Initial.SVD.SensitivityMatrix(Self)
    
    def MainAssembleDyn(Self, Data):
        Self.InitialData(Data.NodesCoord, Data.ElementsEndNodes, Data.IsDOFfree, Data.ElementsType, Data.ElementsA, Data.ElementsE, Data.TensionInit, Data.DynamicMass)



    def MainDynamicRelaxation(Self, Data):

        Self.InitialData(Data.NodesCoord, Data.ElementsEndNodes, Data.IsDOFfree, Data.ElementsType, Data.ElementsA, Data.ElementsE,
                         Data.ElementsLFreeInit, Data.LoadsInit, Data.TensionInit, Data.ReactionsInit,
                         Data.LoadsToApply, Data.LengtheningsToApply, Data.Residual0Threshold)
        Self.DR.InitialData(Data.Dt,
                            Data.AmplMass,
                            Data.MinMass,
                            Data.MaxTimeStep,
                            Data.MaxKEReset)
        Self.DR.Core(Self) # Compute the Dynamic Relaxation Method on the StructureObj
        # GO BACK to MainDynamicRelaxation.py to send the results to C#

    def test_MainDynamicRelaxation(Self, NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                                   ElementsLFreeInit= -1, LoadsInit=np.zeros((0,)),
                                   TensionInit=np.zeros((0,)), ReactionsInit=np.zeros((0,)),
                                   LoadsToApply=np.zeros((0,)), LengtheningsToApply=np.zeros((0,)),
                                   Residual0Threshold=0.0001, Dt=0.01, AmplMass=1, MinMass=0.005, MaxTimeStep=10000,
                                   MaxKEReset=1000):

        Self.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE, ElementsLFreeInit,
                         LoadsInit, TensionInit, ReactionsInit, LoadsToApply, LengtheningsToApply, Residual0Threshold)
        Self.DR.InitialData(Dt,AmplMass,MinMass,MaxTimeStep,MaxKEReset)
        Self.DR.Core(Self)

    def MainLinearDisplacementMethod(Self,Data):
        #initialize inputs and compute the connectivity matrix
        Self.InitialData(Data.NodesCoord, Data.ElementsEndNodes, Data.IsDOFfree, Data.ElementsType, Data.ElementsA, Data.ElementsE,
                         Data.ElementsLFreeInit, Data.LoadsInit, Data.TensionInit, Data.ReactionsInit,
                         Data.LoadsToApply, Data.LengtheningsToApply)

        Self.CoreLinearDisplacementMethod()

    def test_MainLinearDisplacementMethod(Self, NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                                   ElementsLFreeInit=-1, LoadsInit=np.zeros((0,)),
                                   TensionInit=np.zeros((0,)), ReactionsInit=np.zeros((0,)),
                                   LoadsToApply=np.zeros((0,)), LengtheningsToApply=np.zeros((0,))):

        Self.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                         ElementsLFreeInit, LoadsInit, TensionInit, ReactionsInit,
                         LoadsToApply, LengtheningsToApply)

        Self.CoreLinearDisplacementMethod()

    def MainNONLinearDisplacementMethod(Self,Data):
        #initialize inputs and compute the connectivity matrix
        Self.InitialData(Data.NodesCoord, Data.ElementsEndNodes, Data.IsDOFfree, Data.ElementsType, Data.ElementsA, Data.ElementsE,
                         Data.ElementsLFreeInit, Data.LoadsInit, Data.TensionInit, Data.ReactionsInit,
                         Data.LoadsToApply, Data.LengtheningsToApply,n_steps=Data.n_steps)

        Self.CoreNONLinearDisplacementMethod()

    def test_MainNONLinearDisplacementMethod(Self, NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                                   ElementsLFreeInit=-1, LoadsInit=np.zeros((0,)),
                                   TensionInit=np.zeros((0,)), ReactionsInit=np.zeros((0,)),
                                   LoadsToApply=np.zeros((0,)), LengtheningsToApply=np.zeros((0,)),n_steps=100):

        Self.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                         ElementsLFreeInit, LoadsInit, TensionInit, ReactionsInit,
                         LoadsToApply, LengtheningsToApply,n_steps=n_steps)

        Self.CoreNONLinearDisplacementMethod()

    # def test_Main_LinearSolve_Force_Method(Self, NodesCoord, ElementsEndNodes, IsDOFfree, ElementsA, ElementsE, AxialForces_Already_Applied, Loads_To_Apply,Loads_Already_Applied,Elongations_To_Apply):
    #     Self.RegisterData(NodesCoord,ElementsEndNodes,IsDOFfree,ElementsA,ElementsE,AxialForces_Already_Applied,Loads_To_Apply,1,Loads_Already_Applied,Elongations_To_Apply)
    #     Self.Core_LinearSolve_Force_Method()
    #
    # def test_Main_NonLinearSolve_Force_Method(Self,n_steps,NodesCoord, ElementsEndNodes, IsDOFfree, ElementsA, ElementsE, AxialForces_Already_Applied, Loads_To_Apply,Loads_Already_Applied,Elongations_To_Apply):
    #     Self.RegisterData(NodesCoord,ElementsEndNodes,IsDOFfree,ElementsA,ElementsE,AxialForces_Already_Applied,Loads_To_Apply,n_steps,Loads_Already_Applied,Elongations_To_Apply)
    #     Self.Core_NonLinearSolve_Force_Method()
    # endregion

    # region Private Methods : Retrieve the inputs
    def InitialData(Self, NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType=np.zeros((0,)), ElementsA=np.zeros((0, 2)),
                    ElementsE=np.zeros((0, 2)), ElementsLfreeInit = -1, LoadsInit=np.zeros((0,)),
                    TensionInit=np.zeros((0,)), ReactionsInit=np.zeros((0,)), LoadsToApply=np.zeros((0,)),
                    LengtheningsToApply=np.zeros((0,)), Residual0Threshold=0.00001, n_steps=1):

        ### Initialize fundamental datas ###
        if isinstance(NodesCoord, np.ndarray):
            Self.NodesCount = NodesCoord.reshape(-1, 3).shape[0]
            Self.Initial.NodesCoord = NodesCoord.reshape(-1, ) #see StateInitial
        else:
            Self.Initial.NodesCoord = None
            Self.NodesCount = -1

        if isinstance(ElementsEndNodes, np.ndarray):
            Self.ElementsEndNodes = ElementsEndNodes.reshape(-1, 2).astype(int)
            Self.ElementsCount = Self.ElementsEndNodes.shape[0]
        else:
            Self.ElementsEndNodes = None
            Self.ElementsCount = -1

        if isinstance(IsDOFfree, np.ndarray):
            Self.IsDOFfree = IsDOFfree.reshape((-1,)).astype(bool)
            Self.DOFfreeCount = np.sum(np.ones(3 * Self.NodesCount, dtype=int)[Self.IsDOFfree])
            Self.FixationsCount = 3 * Self.NodesCount - Self.DOFfreeCount
        else:
            Self.IsDOFfree = None
            Self.FixationsCount = -1
            Self.DOFfreeCount = -1

        ### Initialize optional datas ###
        Self.C = Self.ConnectivityMatrix(Self.NodesCount,Self.ElementsCount,Self.ElementsEndNodes)
        (Self.Initial.ElementsL, Self.Initial.ElementsCos) = Self.Initial.ElementsLengthsAndCos(Self,Self.Initial.NodesCoord)  # thus calculate the free lengths based on the nodes coordinates


        if isinstance(ElementsType, np.ndarray) and ElementsType.size == Self.ElementsCount:
            Self.ElementsType = ElementsType.reshape((-1,)).astype(int) #-1 if struts, +1 if cables
        else:
            Self.ElementsType = -np.ones((Self.ElementsCount,)) #all struts

        if isinstance(ElementsA, np.ndarray) and ElementsA.size == 2*Self.ElementsCount:
            Self.ElementsA = ElementsA.reshape((-1, 2)) #[AinCompression,AinTension]
        elif isinstance(ElementsA, np.ndarray) and ElementsA.size == 1*Self.ElementsCount:
            AinTensionAndCompression = ElementsA.reshape((-1, 1))
            Self.ElementsA = np.hstack((AinTensionAndCompression,AinTensionAndCompression))
        else:
            Self.ElementsA = None

        if isinstance(ElementsE, np.ndarray) and ElementsE.size == 2*Self.ElementsCount:
            Self.ElementsE = ElementsE.reshape((-1, 2)) #[EinCompression,EinTension]
        elif isinstance(ElementsE, np.ndarray) and ElementsE.size == 1*Self.ElementsCount:
            EinTensionAndCompression = ElementsE.reshape((-1, 1))
            Self.ElementsE = np.hstack((EinTensionAndCompression,EinTensionAndCompression))
        else:
            Self.ElementsE = None




        if isinstance(LoadsInit, np.ndarray) and LoadsInit.size == 3 * Self.NodesCount:
            Self.Initial.Loads = LoadsInit.reshape(-1, )
        else:
            Self.Initial.Loads = np.zeros((3 * Self.NodesCount,))


        if isinstance(TensionInit, np.ndarray) and TensionInit.size == Self.ElementsCount:
            Self.Initial.Tension = TensionInit.reshape((-1,))
        else:
            Self.Initial.Tension = np.zeros((Self.ElementsCount,))


        if isinstance(ReactionsInit, np.ndarray) and ReactionsInit.size == Self.FixationsCount:
            Self.Initial.Reactions = ReactionsInit.reshape(-1, )
        else:
            Self.Initial.Reactions = np.zeros((Self.FixationsCount,))




        if Self.ElementsE.shape == (Self.ElementsCount,2):
            Self.Initial.ElementsE = Self.ElementsInTensionOrCompression(Self.Initial.Tension,Self.ElementsE)
        if Self.ElementsA.shape == (Self.ElementsCount,2):
            Self.Initial.ElementsA = Self.ElementsInTensionOrCompression(Self.Initial.Tension,Self.ElementsA)


        if isinstance(ElementsLfreeInit, np.ndarray) and ElementsLfreeInit.size == Self.ElementsCount:
            Self.Initial.ElementsLFree = ElementsLfreeInit.reshape((-1,))
        else:
            Self.Initial.ElementsLFree = -np.ones((Self.ElementsCount,))

        if (Self.Initial.ElementsLFree < np.zeros((Self.ElementsCount,))).any() or np.any(ElementsLfreeInit == -1):  # if the free lengths are smaller than 0, it means they have not been calculated yet.
            if np.count_nonzero(np.around(Self.Initial.Tension,decimals = 6))>0 : # if some elements are pre-tensionned, make sure the free lengths take it into account
                F = Self.Flexibility(Self.Initial.ElementsE, Self.Initial.ElementsA, Self.Initial.ElementsL) #flexibility with initial length (considered infinite if EA is close to 0)
                EA = Self.Initial.ElementsL/F # stiffness EA of the elements (with zeros replaced by 1e-9)
                Init_strain = Self.Initial.Tension/EA
                Self.Initial.ElementsLFree = Self.Initial.ElementsL/(1+Init_strain)
            else : #there are no initial tension
                Self.Initial.ElementsLFree = Self.Initial.ElementsL.copy()  # thus calculate the free lengths based on the nodes coordinates




        if isinstance(LoadsToApply, np.ndarray) and LoadsToApply.size == 3 * Self.NodesCount:
            Self.LoadsToApply = LoadsToApply.reshape(-1,)
        else:
            Self.LoadsToApply = np.zeros((3 * Self.NodesCount,))


        if isinstance(LengtheningsToApply, np.ndarray) and LengtheningsToApply.size == Self.ElementsCount:
            Self.LengtheningsToApply = LengtheningsToApply.reshape(-1, )
        else:
            Self.LengtheningsToApply = np.zeros((Self.ElementsCount,))

        if Residual0Threshold > 0:
            Self.Residual0Threshold=Residual0Threshold
        else:
            Self.Residual0Threshold=0.00001

        if n_steps >=1:
            Self.n_steps=n_steps
        else:
            Self.n_steps=1
    # endregion


    #region WORK IN PROGRESS
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
            Elements_Cos_Displ = S0.Compute_Elements_Reorientation(Um_i, S0.C, S0.Initial.ElementsLFree)
            (A_nl, A_nl_free, A_nl_fixed) = S0.Compute_NL_Equilibrium_Matrix(Elements_Cos_Displ, S0.C, S0.IsDOFfree)
            G_i = A_nl_free @ t0
            G[:,i] = G_i

        Kg_mod = SVD.Um_free_row @ G
        # DR.Kg = G @ DR.Um_t
        # print(G)
        return G

    def Compute_Elements_Reorientation(S0,Displacements,C,Elements_L0):
        """
        Calculates the Lines properties (Lengths, CosDir) based on the given NodesCoord and Connectivity Matrix C, and store it in DR
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
            TensionInit: Initial AxialForces in equilibrium in the structure (Bx1)
            LoadsToApply: Loads to apply on the nodes (Nx3)
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
        # IncrR = np.zeros((DR.FixationsCount,1)) #Incr of Reaction at this step.

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

    #endregion WORK IN PROGRESS





    # region DYNAMICS
    def InitializeDynamic(Self,Data):#Initialize all the data for the dynamic computation

        Self.Initial.NodesCoord = Data.NodesCoord
        Self.ElementsType = Data.ElementsType
        Self.ElementsEndNodes = Data.ElementsEndNodes
        Self.ElementsA = Data.ElementsA
        Self.ElementsE = Data.ElementsE
        Self.MaxFreqWanted = Data.MaxFreqWanted
        Self.NodesCount = Data.NodesCoord.reshape(-1, 3).shape[0]
        Self.ElementsCount = Self.ElementsEndNodes.shape[0]
        Self.IsDOFfree = Data.IsDOFfree
        Self.Initial.Tension = Data.TensionInit
        Self.DOFfreeCount = np.sum(np.ones(3 * Self.NodesCount, dtype=int)[Self.IsDOFfree])
        Self.FixationsCount = 3 * Self.NodesCount - Self.DOFfreeCount

        Self.DynMasses = Data.DynamicMass
        Self.MaxFreqWanted = Data.MaxFreqWanted

    def ModuleDynamics(Self,Data): #Data ? DynamicMass,MaxFreqWanted
        #LUMPED MASS MATRIX
        #Used via C# for the dynamic computation
        """
        Test the function before using the module that compute the natural frequency for a certain prestress and mass on the given geometry
        Input:
            :param NodesCoord : coordinates of the nodes
            :param prestrainLevel : Applied prestress in [kN] - constant
            :param Masses : Masses at each node [Kg] - [ integer ] (LUMPED MODEL)
            :param Applied Prestress

            :return omega : array containing the natural frequencies of the structure
            :return PHI : vector containing the modes for each natural frequency
            #The returns are sorted from small to large frequencies

        """


        Self.InitializeDynamic(Data)

        Self.C = Self.ConnectivityMatrix( Self.NodesCount, Self.ElementsCount, Self.ElementsEndNodes)
        Self.DOFfreeCount = 3 * Self.NodesCount - Self.FixationsCount

        #We consider here the initial shape of the structure : underformed due to prestress or external loads
    
        #Self.Initial.NodesCoord
        (l, ElementsCos) = Self.Initial.ElementsLengthsAndCos(Self, Self.Initial.NodesCoord) # Compute the length and the cosinus director in the initial geomety of the struture
        #(A, AFree, AFixed) = Self.Initial.EquilibriumMatrix(Self, ElementsCos) # Compute the equilibrium matrix in the initial state [All dof, free dof, fixed dof]
        
        #Retrive the Young Modulus and areas in function of the caracter of the internal forces of the members : tension or compression
        Self.Initial.ElementsE = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsE)
        Self.Initial.ElementsA = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsA)
        
        
        #The tension in the structure contain already the influence of the load and the pretension due to Lfree < L


        # Compute the K_geo - the rigidity matrix due to the Prestress
            #1 - Compute the force densities for each member  - Q [ #member] = F/l [N/m]
            #The forces can come from the pretension (Lfree) or the applied load

        Q = Self.Initial.ForceDensities(Self.Initial.Tension , l) #take the initial tension

            # 2 - Obtain a list containing the local rigidity matrix for each member
        kgLocList = Self.Initial.GeometricLocalStiffnessList(Self, Q)
            #3 - Construct the global stiffness matrix of the structure
        Kgeo = Self.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Self.IsDOFfree].T[Self.IsDOFfree].T # Obtain the Final matrix with only the free DOF

        # Compute the K_mat - the rigidity matrix linked to the material rigidity
        # The material rigidity is only axial
        # Consider that each node is hinged

            # 1 - obtain the list of the local K_mat of each member
        kmatLocList = Self.Initial.MaterialLocalStiffnessList(Self, l, ElementsCos, Self.Initial.ElementsA,
                                                                Self.Initial.ElementsE)
            # 2 - Obtain the global stiffness matrix of the structure
        Kmat = Self.LocalToGlobalStiffnessMatrix(kmatLocList)
        KmatFree = Kmat[Self.IsDOFfree].T[Self.IsDOFfree].T

        KFree = KmatFree + KgeoFree # [N/m]

        # Used units
        # K_geo = [N/m]
        # K_mat = [N/m]

        # Mass matrix used for the dynamics part
        # Need to use Masses from "DynMasses" variable
        # "DynMasses" [ # of nodes]

        ##MassesDirection = np.repeat(Data.DynMasses,3) # Vector [3* # Nodes] containing in each direction the dynamic mass
        # MassesDOF is made the most general : 3 dimensions
        # The masses for each DOF is obtained by decreasing the size of the MassesDiag size
        ##MassesDiag = np.diag(MassesDirection) # Contain all the directions


        Self.DynMasses = np.abs(Self.DynMasses)

        if len(Self.DynMasses) != Self.NodesCount: #The length need to be equal to the number of nodes
            Self.DynMasses = np.ones(Self.NodesCount)

        
        if np.any(Self.DynMasses,0) == False: #No mass equal to zero in the vector
            Self.DynMasses = np.ones(Self.NodesCount)

        MassesDiag = np.diag(np.repeat(Self.DynMasses,3))
        MassesDiagFree = MassesDiag[Self.IsDOFfree].T[Self.IsDOFfree].T #Retrieve the masses linked to free direction, DOF


        # Compute the eigen values of the problem - natural frequencies
        # Made via the characteristic equation : det ( K - \omega_i M ) = 0

        w2, PHI = np.linalg.eig(np.linalg.inv(MassesDiagFree)@KFree) #squared natural frequencies and the modes
        w = np.sqrt(w2)

        # Sort the frequencies and the modes from small to high frequencies
        # Convention
        idx = w.argsort()[::1]
        w = w[idx]
        PHI = PHI[:, idx]
        
        #Insert the results
        Self.freq = w/(2*np.pi) 
        Self.mode = PHI


        #TotMode : insert all the displacement of the mode considering that for the Non DOF that the displacement is zero
        Self.TotMode = np.zeros((len(Self.IsDOFfree),Self.DOFfreeCount))
        Self.TotMode[Self.IsDOFfree] = Self.mode
        
        #Return a part of the computed elements in function of the value of MaxFreqWanted
        if Self.MaxFreqWanted != 0:
            if Self.MaxFreqWanted < Self.DOFfreeCount:
                Self.freq = Self.freq[:Self.MaxFreqWanted]
                Self.mode = Self.mode[:,:Self.MaxFreqWanted]
                Self.TotMode = Self.TotMode[:,:Self.MaxFreqWanted]

            else:
                Self.MaxFreqWanted = Self.DOFfreeCount
        else:
            Self.MaxFreqWanted = Self.DOFfreeCount
        


    def InitializeDynamic_CONSISTENT(Self,Data):#Initialize all the data for the dynamic computation

        Self.Initial.NodesCoord = Data.NodesCoord
        Self.ElementsType = Data.ElementsType
        Self.ElementsEndNodes = Data.ElementsEndNodes
        Self.ElementsA = Data.ElementsA
        Self.ElementsE = Data.ElementsE
        Self.MaxFreqWanted = Data.MaxFreqWanted
        Self.NodesCount = Data.NodesCoord.reshape(-1, 3).shape[0]
        Self.ElementsCount = Self.ElementsEndNodes.shape[0]
        Self.IsDOFfree = Data.IsDOFfree
        Self.Initial.Tension = Data.TensionInit
        Self.DOFfreeCount = np.sum(np.ones(3 * Self.NodesCount, dtype=int)[Self.IsDOFfree])
        Self.FixationsCount = 3 * Self.NodesCount - Self.DOFfreeCount

        Self.DynMasses = Data.DynamicMass
        Self.MassElement = Data.MassElement
        Self.MaxFreqWanted = Data.MaxFreqWanted


    def ModuleDynamics_CONSISTENT(Self,Data): #Data ? DynamicMass,MaxFreqWanted
        #CONSISTENT MASS MATRIX
        #Used via C# for the dynamic computation
        """
        Test the function before using the module that compute the natural frequency for a certain prestress and mass on the given geometry
        Input:
            :param NodesCoord : coordinates of the nodes
            :param prestrainLevel : Applied prestress in [kN] - constant
            :param Masses : Masses at each node [Kg] - [ integer ] (CONSISTENT MODEL)
            :param Applied Prestress

            :return omega : array containing the natural frequencies of the structure
            :return PHI : vector containing the modes for each natural frequency
            #The returns are sorted from small to large frequencies

        """


        Self.InitializeDynamic_CONSISTENT(Data)

        Self.C = Self.ConnectivityMatrix( Self.NodesCount, Self.ElementsCount, Self.ElementsEndNodes)
        Self.DOFfreeCount = 3 * Self.NodesCount - Self.FixationsCount

        #We consider here the initial shape of the structure : underformed due to prestress or external loads
    
        #Self.Initial.NodesCoord
        (l, ElementsCos) = Self.Initial.ElementsLengthsAndCos(Self, Self.Initial.NodesCoord) # Compute the length and the cosinus director in the initial geomety of the struture
        #(A, AFree, AFixed) = Self.Initial.EquilibriumMatrix(Self, ElementsCos) # Compute the equilibrium matrix in the initial state [All dof, free dof, fixed dof]
        
        #Retrive the Young Modulus and areas in function of the caracter of the internal forces of the members : tension or compression
        Self.Initial.ElementsE = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsE)
        Self.Initial.ElementsA = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsA)
        
        
        #The tension in the structure contain already the influence of the load and the pretension due to Lfree < L


        # Compute the K_geo - the rigidity matrix due to the Prestress
            #1 - Compute the force densities for each member  - Q [ #member] = F/l [N/m]
            #The forces can come from the pretension (Lfree) or the applied load

        Q = Self.Initial.ForceDensities(Self.Initial.Tension , l) #take the initial tension

            # 2 - Obtain a list containing the local rigidity matrix for each member
        kgLocList = Self.Initial.GeometricLocalStiffnessList(Self, Q)
            #3 - Construct the global stiffness matrix of the structure
        Kgeo = Self.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Self.IsDOFfree].T[Self.IsDOFfree].T # Obtain the Final matrix with only the free DOF

        # Compute the K_mat - the rigidity matrix linked to the material rigidity
        # The material rigidity is only axial
        # Consider that each node is hinged

            # 1 - obtain the list of the local K_mat of each member
        kmatLocList = Self.Initial.MaterialLocalStiffnessList(Self, l, ElementsCos, Self.Initial.ElementsA,
                                                                Self.Initial.ElementsE)
            # 2 - Obtain the global stiffness matrix of the structure
        Kmat = Self.LocalToGlobalStiffnessMatrix(kmatLocList)
        KmatFree = Kmat[Self.IsDOFfree].T[Self.IsDOFfree].T

        KFree = KmatFree + KgeoFree  # [N/m]

        # Used units
        # K_geo = [N/m]
        # K_mat = [N/m]

        # Mass matrix used for the dynamics part
        # Need to use Masses from "DynMasses" variable
        # "DynMasses" [ # of nodes]

        ##MassesDirection = np.repeat(Data.DynMasses,3) # Vector [3* # Nodes] containing in each direction the dynamic mass
        # MassesDOF is made the most general : 3 dimensions
        # The masses for each DOF is obtained by decreasing the size of the MassesDiag size
        ##MassesDiag = np.diag(MassesDirection) # Contain all the directions


        Self.DynMasses = np.abs(Self.DynMasses)

        if len(Self.DynMasses) != Self.NodesCount: #The length need to be equal to the number of nodes
            Self.DynMasses = np.ones(Self.NodesCount)

        
        if np.any(Self.DynMasses,0) == False: #No mass equal to zero in the vector
            Self.DynMasses = np.ones(Self.NodesCount)

        MassesDiagNodale = np.diag(np.repeat(Self.DynMasses,3))

        MassesElementMatrix = np.zeros((Self.NodesCount*3,Self.NodesCount*3))

        if len(Self.MassElement) == Self.ElementsCount:

            for i in range(Self.ElementsCount):
                MassToAdd = Self.MassElement[i]
                Node1 = Self.ElementsEndNodes[i,0]
                Node2 = Self.ElementsEndNodes[i,1]
                index = np.array([3 * Node1, 3 * Node1 + 1, 3 * Node1 + 2,
                              3 * Node2, 3 * Node2 + 1, 3 * Node2 + 2]).astype(int)
                indexBis = np.array([3 * Node2, 3 * Node2 + 1, 3 * Node2 + 2,
                              3 * Node1, 3 * Node1 + 1, 3 * Node1 + 2]).astype(int)
                for j in range(6):
                    MassesElementMatrix[index[j],index[j]] += 1/3*MassToAdd
                    MassesElementMatrix[index[j],indexBis[j]] += 1/6*MassToAdd

        
        MassesDiag = MassesDiagNodale + MassesElementMatrix #The matrix is not symmetric

        MassesDiagFree = MassesDiag[Self.IsDOFfree].T[Self.IsDOFfree].T #Retrieve the masses linked to free direction, DOF


        # Compute the eigen values of the problem - natural frequencies
        # Made via the characteristic equation : det ( K - \omega_i M ) = 0

        w2, PHI = np.linalg.eig(np.linalg.inv(MassesDiagFree)@KFree) #squared natural frequencies and the modes
        w = np.sqrt(w2)

        # Sort the frequencies and the modes from small to high frequencies
        # Convention
        idx = w.argsort()[::1]
        w = w[idx]
        PHI = PHI[:, idx]
        
        #Insert the results
        Self.freq = w/(2*np.pi) 
        Self.mode = PHI


        #TotMode : insert all the displacement of the mode considering that for the Non DOF that the displacement is zero
        Self.TotMode = np.zeros((len(Self.IsDOFfree),Self.DOFfreeCount))
        Self.TotMode[Self.IsDOFfree] = Self.mode
        
        #Return a part of the computed elements in function of the value of MaxFreqWanted
        if Self.MaxFreqWanted != 0:
            if Self.MaxFreqWanted < Self.DOFfreeCount:
                Self.freq = Self.freq[:Self.MaxFreqWanted]
                Self.mode = Self.mode[:,:Self.MaxFreqWanted]
                Self.TotMode = Self.TotMode[:,:Self.MaxFreqWanted]

            else:
                Self.MaxFreqWanted = Self.DOFfreeCount
        else:
            Self.MaxFreqWanted = Self.DOFfreeCount





    def test_ModuleDynamics(Self,NodesCount,ElementsCount,ElementsEndNodes,FixationsCount,NodesCoord,ElementsType,ElementsE,ElementsA,TensionInit,IsDOFfree,DynamicMass,NumberOfFreqWanted): 
        
        """
        Test the function before using the module that compute the natural frequency for a certain prestress and mass on the given geometry

        """
        #assert Data.DynMasses.shape == (Self.NodesCount, )
        #Initialize all the data
        Self.NodesCount = NodesCount
        Self.ElementsCount = ElementsCount
        Self.ElementsEndNodes = ElementsEndNodes
        Self.FixationsCount = FixationsCount
        Self.ElementsA = ElementsA
        Self.ElementsE = ElementsE
        Self.ElementsType = ElementsType
        Self.IsDOFfree = IsDOFfree
        Self.DynMasses = DynamicMass

        Self.C = Self.ConnectivityMatrix(Self.NodesCount, Self.ElementsCount, Self.ElementsEndNodes)
        Self.DOFfreeCount = 3 * Self.NodesCount - Self.FixationsCount
        print('1',Self.C)
        #We consider here the initial shape of the structure : underformed due to prestress or external loads
        (l, ElementsCos) = Self.Initial.ElementsLengthsAndCos(Self,NodesCoord) # Compute the length and the cosinus director in the initial geomety of the struture
        #(A, AFree, AFixed) = Self.Initial.EquilibriumMatrix(Self,ElementsCos) # Compute the equilibrium matrix in the initial state [All dof, free dof, fixed dof]
        print('2')
        #Retrive the Young Modulus and areas in function of the caracter of the internal forces of the members : tension or compression
        Self.Initial.ElementsE = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsE)
        Self.Initial.ElementsA = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsA)
        print('3')
        #The tension in the structure contain already the influence of the load and the pretension due to Lfree < L


        # Compute the K_geo - the rigidity matrix due to the Prestress
            #1 - Compute the force densities for each member  - Q [ #member] = F/l [N/m]
            #The forces can come from the pretension (Lfree) or the applied load
        #TensionInit in N
        Q = Self.Initial.ForceDensities(TensionInit , l)

            # 2 - Obtain a list containing the local rigidity matrix for each member
        kgLocList = Self.Initial.GeometricLocalStiffnessList(Self, Q)
            #3 - Construct the global stiffness matrix of the structure
        Kgeo = Self.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Self.IsDOFfree].T[Self.IsDOFfree].T # Obtain the Final matrix with only the free DOF

        # Compute the K_mat - the rigidity matrix linked to the material rigidity
        # The material rigidity is only axial
        # Consider that each node is hinged

            # 1 - obtain the list of the local K_mat of each member
        kmatLocList = Self.Initial.MaterialLocalStiffnessList(Self, l, ElementsCos, Self.Initial.ElementsA,
                                                                Self.Initial.ElementsE)
            # 2 - Obtain the global stiffness matrix of the structure
        Kmat = Self.LocalToGlobalStiffnessMatrix(kmatLocList)
        KmatFree = Kmat[Self.IsDOFfree].T[Self.IsDOFfree].T

        KFree = KgeoFree + KmatFree # [N/m]

        # Used units
        # K_geo = [N/m]
        # K_mat = [N/m]

        # Mass matrix used for the dynamics part
        # Need to use Masses from "DynMasses" variable
        # "DynMasses" [ # of nodes]

        ##MassesDirection = np.repeat(Data.DynMasses,3) # Vector [3* # Nodes] containing in each direction the dynamic mass
        # MassesDOF is made the most general : 3 dimensions
        # The masses for each DOF is obtained by decreasing the size of the MassesDiag size
        ##MassesDiag = np.diag(MassesDirection) # Contain all the directions
        print('4')
        Self.DynMasses = np.abs(Self.DynMasses)
        print('5')
        if len(Self.DynMasses) != Self.NodesCount: #The length need to be equal to the number of nodes
            Self.DynMasses = np.ones(Self.NodesCount)
        print('6')
        
        if np.any(Self.DynMasses,0) == False: #No mass equal to zero in the vector
            Self.DynMasses = np.ones(Self.NodesCount)
            print('in')
        print('7')
        MassesDiag = np.diag(np.repeat(Self.DynMasses,3))
        MassesDiagFree = MassesDiag[Self.IsDOFfree].T[Self.IsDOFfree].T #Retrieve the masses linked to free direction, DOF
        print('8')

        # Compute the eigen values of the problem - natural frequencies
        # Made via the characteristic equation : det ( K - \omega_i M ) = 0

        w2, PHI = np.linalg.eig(np.linalg.inv(MassesDiagFree)@KFree) #squared natural frequencies and the modes
        w = np.sqrt(w2)

        # Sort the frequencies and the modes from small to high frequencies
        # Convention

        idx = w.argsort()[::1]
        w = w[idx]
        PHI = PHI[:, idx]

        freq = w/(2*np.pi)
        mode = PHI
  
        #TotMode : insert all the displacement of the mode considering that for the Non DOF, the displacement is zero
        TotMode = np.zeros((len(Self.IsDOFfree),len(freq)))
        TotMode[Self.IsDOFfree] = mode

        if NumberOfFreqWanted != 0:
            if NumberOfFreqWanted < Self.DOFfreeCount:
                freq = freq[:NumberOfFreqWanted]
                mode = mode[:,:NumberOfFreqWanted]
                TotMode = TotMode[:,:NumberOfFreqWanted]
 
        return freq,mode,TotMode
    #endregion

