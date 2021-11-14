# -*- coding: utf-8 -*-
import unittest
from StructureObj import *
import numpy as np

class StructureObj_Tests(unittest.TestCase):


    # region Simple tests on 2 cables (*--c1--*--c2--*)

    # region Assemble methods
    def test_RegisterData_2cables(self):
        """
        test to check that RegisterData calculates correctly the number of nodes, elements, and supports. Test for 2 cables
        """
        S0 = StructureObj()
        NodesCoord = np.array([[0.0,1.0,0.0],[1.0,1.0,0.0],[2.0,1.0,0.0]])
        Elements_ExtremitiesIndex = np.array([[0,1],[1,2]])
        IsDOFfree = np.array([False,False,False,True,True,True,False,False,False])

        S0.RegisterData(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree)
        # print(S0.NodesCount)
        # print(S0.ElementsCount)
        # print(S0.FixationsCount)
        # print(S0.DOFfreeCount)
        self.assertEqual(S0.NodesCount, 3)
        self.assertEqual(S0.ElementsCount, 2)
        self.assertEqual(S0.FixationsCount, 6)
        self.assertEqual(S0.DOFfreeCount, 3)

    def test_Connectivity_Matrix_2cables(self):
        """
        test to see if the computation of the connectivity_matrix of 2 cables (*--c1--*--c2--*) works
        """
        S0 = StructureObj() #empty object

        #required input for the method
        ElementsCount = 2
        NodesCount = 3
        Elements_ExtremitiesIndex = np.array([[0,1],[1,2]])

        C = S0.Connectivity_Matrix(NodesCount,ElementsCount,Elements_ExtremitiesIndex) #test the method

        #check the results
        success = (C == np.array([[-1,  1,  0],[ 0, -1, 1]])).all()
        self.assertEqual(success, True)

    def test_Compute_Elements_Geometry_2cables(self):
        """
        test to check that Compute_Elements_Geometry calculates correctly the lengths of the elements and their cos directors compareed to Grasshopper results. Test for 2 cables (*--c1--*--c2--*)
        """
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, True, True, False, False, False])

        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree)
        S0.C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)

        (S0.Elements_L,S0.Elements_Cos) = S0.Compute_Elements_Geometry(S0.NodesCoord,S0.C)

        #check the results
        # test of comparison with Grasshopper
        Elements_L0_GH = np.array([1.0,1.0])
        Cos_X_GH = np.array([1.0, 1.0])
        Cos_Y_GH = np.array([0.0, 0.0])
        Cos_Z_GH = np.array([0.0, 0.0])

        successL = (S0.Elements_L == Elements_L0_GH).all()
        successCosX = (S0.Elements_Cos[:,0] == Cos_X_GH).all()
        successCosY = (S0.Elements_Cos[:,1] == Cos_Y_GH).all()
        successCosZ = (S0.Elements_Cos[:,2] == Cos_Z_GH).all()

        self.assertEqual(successL, True)
        self.assertEqual(successCosX, True)
        self.assertEqual(successCosY, True)
        self.assertEqual(successCosZ, True)

    def test_Compute_Equilibrium_Matrix_2cables(self):
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, True, True, False, False, False])

        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree)
        C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (l,Elements_Cos) = S0.Compute_Elements_Geometry(NodesCoord,C)
        (A, A_free, A_fixed) = S0.Compute_Equilibrium_Matrix(Elements_Cos,C,IsDOFfree)

        A_free_answer = np.array([[1.0, -1.0], [0.0, 0.0], [0.0, 0.0]])
        success  = (A_free == A_free_answer).all()

        self.assertEqual(success,True)

    def test_SVD_Equilibrium_Matrix_2cables(self):
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, True, True, False, False, False])

        S0.RegisterData(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree)
        C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (l, Elements_Cos) = S0.Compute_Elements_Geometry(NodesCoord, C)
        (A, A_free, A_fixed) = S0.Compute_Equilibrium_Matrix(Elements_Cos,C, IsDOFfree)
        SVD = S0.SVD_Equilibrium_Matrix(A_free)

        r_answer = 1
        self.assertEqual(SVD.r, r_answer)

        s_answer = 1
        self.assertEqual(SVD.s, s_answer)

        SS_answer = np.array([[-1.0, -1.0]])
        successSS = np.allclose(SVD.SS,SS_answer)
        self.assertEqual(successSS, True)

        m_answer = 2
        self.assertEqual(SVD.m, m_answer)

        Um_answer= np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        successUm = np.allclose(SVD.Um_free_row,Um_answer)
        self.assertEqual(successUm, True)

    def test_Compute_StiffnessMat_Matrix_2cables(self):
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, True, True, False, False, False])

        S0.RegisterData(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree)
        C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (Elements_L, Elements_Cos) = S0.Compute_Elements_Geometry(NodesCoord, C)
        (A, A_free, A_fixed) = S0.Compute_Equilibrium_Matrix(Elements_Cos,C, IsDOFfree)

        Elements_A = np.array([0.002500,0.002500])
        Elements_E = np.array([10000000000.0,10000000000.0])

        Km  = S0.Compute_StiffnessMat_Matrix(A,Elements_L,Elements_A,Elements_E)
        Km_free = S0.Compute_StiffnessMat_Matrix(A_free, Elements_L, Elements_A, Elements_E)

        Km_free_answer= np.zeros((S0.DOFfreeCount,S0.DOFfreeCount))
        Km_free_answer[0,0] = Elements_A @ Elements_E.transpose()
        successKm = np.allclose(Km_free,Km_free_answer)
        self.assertEqual(successKm, True)


    # endregion

    # region NonLinear Methods
    def test_Main_NonLinearSolve_Disp_Meth_2cables(self):
        #cfr master thesis Jferon
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False])
        Loads_To_Apply = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -100000.0], [0.0, 0.0, 0.0]]).reshape((-1,))

        Elements_A = np.array([0.002500, 0.002500])*1e6
        Elements_E = np.array([10000000000.0, 10000000000.0])/1e6
        AxialForces_Already_Applied = np.array([])

        S0.test_Main_NonLinearSolve_Displ_Method(100, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                                 AxialForces_Already_Applied, Loads_To_Apply)

        last_step = S0.Stages.size - 1

        d_obtained = S0.Displacements_Results[3*1+2,last_step]
        d_sol = -158.74 * 1e-3 #analytique solution
        err = 2/100 # admissible error
        d_adm = [d_sol*(1+err),d_sol*(1-err)] # admissible interval
        successD = d_obtained>=d_adm[0] and d_obtained<=d_adm[1]
        self.assertEqual(successD, True)

        N_obtained = S0.AxialForces_Results[:,last_step]
        N_sol = 313020 #analytique solution
        err = 2/100 # admissible error
        N_adm = [N_sol*(1-err),N_sol*(1+err)] # admissible interval
        successN = N_obtained[0] >=N_adm[0] and N_obtained[0]<=N_adm[1] and N_obtained[1] >=N_adm[0] and N_obtained[1]<=N_adm[1]
        self.assertEqual(successN, True)

        # Reactions_answer = np.array([50000, 0, 50000, 0, -50000, 0, 50000])  # analytique solution
        # self.assertEqual(np.allclose(S0.Reactions_Results, Reactions_answer), True)

    def test_Main_NonLinearSolve_Disp_Meth_2cables_3LoadStages(self):
        #cfr solution in excel files attached
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [2.0, 0.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False])
        Elements_A = np.array([0.000050, 0.000050])*1e6
        Elements_E = np.array([100, 100])*1e3

        AxialForces_To_Apply = np.array([20000, 20000])
        #we need a function to pass from axialforces to prestressloads (see in c#)
        PrestressLoads_To_Apply = np.array([[20000.0, 0.0, 0.0], [0.0, 0.0, 0.0], [-20000.0, 0.0, 0.0]]).reshape((-1,))

        S0.test_Main_LinearSolve_Displ_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E, [], PrestressLoads_To_Apply)

        AxialForces_Already_Applied = S0.AxialForces_Results+AxialForces_To_Apply.reshape((-1,1))
        Loads_To_Apply1 = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -5109.0], [0.0, 0.0, 0.0]]).reshape((-1,))

        S1 = StructureObj()
        S1.test_Main_NonLinearSolve_Displ_Method(100, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                                 AxialForces_Already_Applied, Loads_To_Apply1)

        last_step = S1.Stages.size - 1

        d_obtained = S1.Displacements_Results[3*1+2,last_step]
        d_sol1 = -75.0 * 1e-3 #analytique solution
        err = 2/100 # admissible error
        d_adm = [d_sol1*(1+err),d_sol1*(1-err)] # admissible interval
        successD = d_obtained>=d_adm[0] and d_obtained<=d_adm[1]
        self.assertEqual(successD, True)

        N_obtained = S1.AxialForces_Results[:,last_step].reshape((-1,1)) + AxialForces_Already_Applied
        N_sol = 34043 #analytique solution
        err = 2/100 # admissible error
        N_adm = [N_sol*(1-err),N_sol*(1+err)] # admissible interval
        successN = N_obtained[0] >=N_adm[0] and N_obtained[0]<=N_adm[1] and N_obtained[1] >=N_adm[0] and N_obtained[1]<=N_adm[1]
        self.assertEqual(successN, True)


        AxialForces_Already_Applied2 = N_obtained
        Loads_To_Apply2 = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -9988.0], [0.0, 0.0, 0.0]]).reshape((-1,)) - Loads_To_Apply1
        NodesCoord2 = S1.NodesCoord+S1.Displacements_Results[:,last_step].reshape((-1,1))

        S2 = StructureObj()
        S2.test_Main_NonLinearSolve_Displ_Method(100, NodesCoord2, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                                 AxialForces_Already_Applied2, Loads_To_Apply2)

        last_step2 = S2.Stages.size - 1

        d_obtained2 = S2.Displacements_Results[3*1+2,last_step2] + S2.NodesCoord[3*1+2]
        d_sol2 = -105.0 * 1e-3 #analytique solution
        err = 2/100 # admissible error
        d_adm2 = [d_sol2*(1+err),d_sol2*(1-err)] # admissible interval
        successD2 = d_obtained2>=d_adm2[0] and d_obtained2<=d_adm2[1]
        self.assertEqual(successD2, True)

        N_obtained2 = S2.AxialForces_Results[:,last_step2].reshape((-1,1)) + AxialForces_Already_Applied2
        N_sol2 = 47487 #analytique solution
        err = 2/100 # admissible error
        N_adm2 = [N_sol2*(1-err),N_sol2*(1+err)] # admissible interval
        successN2 = N_obtained2[0] >=N_adm2[0] and N_obtained2[0]<=N_adm2[1] and N_obtained2[1] >=N_adm2[0] and N_obtained2[1]<=N_adm2[1]
        self.assertEqual(successN2, True)

    # def test_LinearSolve_Force_Method_2cables(self):
    #     """
    #     test to check that RegisterData calculates correctly the number of nodes, elements, and supports. Test for 3 cables
    #     """
    #     S0 = StructureObj()
    #     L = 2*5.08
    #     # l = L/3 # length of the middle cable
    #     # l1 = np.sqrt(H**2 + l**2) # length of the extreme cables
    #     # cos = l/l1
    #     # sin = H/l1
    #     NodesCoord = np.array([[0.0,0.0,0.0],[L/2,0.0,0.0],[L,0.0,0.0]])
    #     ElementsEndNodes = np.array([[0,1],[1,2]])
    #     IsDOFfree = np.array([False,False,False,True,False,True,False,False,False])
    #
    #     # note that results are independant from EA since statically determinate
    #     A = 1 # mm²
    #     E = 564.92 # MPa
    #     ElementsA = np.array([A,A])
    #     ElementsE = np.array([E,E])
    #
    #     # initial forces. note that results are independant from W since ?
    #     W = 311.38 #N
    #     t0 = 4448.2 #N
    #     Loads_Already_Applied = np.array([[0.0,0.0,0.0],[0.0,0.0,0.0],[0.0,0.0,0.0]])
    #     AxialForces_Already_Applied = np.array([t0,t0])
    #     Loads_To_Apply = np.array([[0.0,0.0,0.0],[0.0,0.0,-W],[0.0,0.0,0.0]])
    #     Elongations_To_Apply = np.array([0,0])
    #
    #     S0.test_Main_LinearSolve_Force_Method(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsA, ElementsE,
    #                                        AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
    #                                        Elongations_To_Apply)
    #
    #     Displacements_answer_free = np.array([0,166.54])*1e-3 #analytique solution
    #     Displacements_answer = np.zeros((9, 1))
    #     Displacements_answer[IsDOFfree] = Displacements_answer_free.reshape(-1,1)
    #     self.assertEqual(np.allclose(S0.Displacements_Results,Displacements_answer,atol=1e-5),True)

    def test_Main_NonLinearSolve_Disp_Meth_3cables_NLprestress(self):
        #cfr master thesis Jferon
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0], [2.0, 0.0, 0.0], [4.0, 0.0, 0.0], [2.0, 0.0, -1.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2], [1, 3]])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False, False, False, False])
        Loads_To_Apply = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -446068.4], [0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]).reshape((-1,))
        Elements_A = np.array([50.27, 50.27, 50.27]) #mm²
        Elements_E = np.array([70000, 70000, 70000]) #MPa
        AxialForces_Already_Applied = np.array([])

        S0.test_Main_NonLinearSolve_Displ_Method(100, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                                 AxialForces_Already_Applied, Loads_To_Apply)

        last_step = S0.Stages.size - 1

        d_obtained = S0.Displacements_Results[3*1+2,last_step]
        d_sol = -126.55 * 1e-3 #analytique solution
        err = 2/100 # admissible error
        d_adm = [d_sol*(1+err),d_sol*(1-err)] # admissible interval
        successD = d_obtained>=d_adm[0] and d_obtained<=d_adm[1]
        self.assertEqual(successD, True)



        # N_obtained = S0.AxialForces_Results[:,last_step]
        # N_sol = np.array([7037.17,7037.17,888.81]) #analytique solution
        # err = 2/100 # admissible error
        # N_adm = [N_sol*(1-err),N_sol*(1+err)] # admissible interval
        # successN = N_obtained[0] >=N_adm[0] and N_obtained[0]<=N_adm[1] and N_obtained[1] >=N_adm[0] and N_obtained[1]<=N_adm[1]
        # self.assertEqual(False, True)

        # Reactions_answer = np.array([50000, 0, 50000, 0, -50000, 0, 50000])  # analytique solution
        # self.assertEqual(np.allclose(S0.Reactions_Results, Reactions_answer), True)


    # endregion

    # endregion

    # region Simple tests on 2 bars /\ (cfr Annexe A1.1.1 of J.Feron Master thesis (p103 of pdf))

    def test_Compute_StiffnessMatGeo_Matrix_2bars(self):
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 1.0], [2.0, 0.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False])

        Elements_A = np.array([0.002500, 0.002500])
        Elements_E = np.array([10000000000.0, 10000000000.0])

        S0.RegisterData(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E)
        C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)

        #1) Compute Elements Geometry
        (Elements_L, Elements_Cos) = S0.Compute_Elements_Geometry(S0.NodesCoord, C)

        # 2) Compute stiffness matrices
        (List_km_loc, List_kg_loc) = S0.Compute_StiffnessMatGeo_LocalMatrices(Elements_L, Elements_Cos, S0.ElementsA, S0.ElementsE, S0.AxialForces_Already_Applied)
        K = S0.Compute_StiffnessMatGeo_Matrix(List_km_loc,List_kg_loc) # (3n+c,3n+c) mat+geo (but here Geo is null)

        # 3) Cross checks
        # a) Elements Geometry
        rac_2 = np.sqrt(2)
        Elements_L0_GH = np.array([rac_2,rac_2])
        Cos_X_GH = np.array([1/rac_2, 1/rac_2])
        Cos_Y_GH = np.array([0.0, 0.0])
        Cos_Z_GH = np.array([1/rac_2, -1/rac_2])

        successL = np.allclose(Elements_L,Elements_L0_GH)
        successCosX = np.allclose(Elements_Cos[:,0],Cos_X_GH)
        successCosY = np.allclose(Elements_Cos[:,1],Cos_Y_GH)
        successCosZ = np.allclose(Elements_Cos[:,2],Cos_Z_GH)

        self.assertEqual(successL, True)
        self.assertEqual(successCosX, True)
        self.assertEqual(successCosY, True)
        self.assertEqual(successCosZ, True)

        # b) cross check with the material matrix computed from force Method
        (A, A_free, A_fixed) = S0.Compute_Equilibrium_Matrix(Elements_Cos,C, S0.IsDOFfree)
        Km  = S0.Compute_StiffnessMat_Matrix(A, Elements_L, S0.ElementsA, S0.ElementsE) # (3n,3n) mat only

        n = NodesCoord.shape[0]
        successK = np.allclose(K[:3*n,:3*n], Km)
        self.assertEqual(successK, True)

    def test_Main_LinearSolve_Disp_Meth_2bars(self):

        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 1.0], [2.0, 0.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False])
        Loads_To_Apply = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -100000.0], [0.0, 0.0, 0.0]])

        Elements_A = np.array([0.002500, 0.002500])
        Elements_E = np.array([10000000000.0, 10000000000.0])
        AxialForces_Already_Applied = np.array([])

        S0.test_Main_LinearSolve_Displ_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                              AxialForces_Already_Applied, Loads_To_Apply)

        self.assertAlmostEqual(S0.Displacements_Results.reshape((-1,3))[1,2],-5.657*1e-3,6)

        Forces_answer = np.array([-70711,-70711]) #analytique solution
        self.assertEqual(np.allclose(S0.AxialForces_Results,Forces_answer),True)

        Reactions_answer = np.array([50000,0,50000,0,-50000,0,50000])  # analytique solution
        self.assertEqual(np.allclose(S0.Reactions_Results.reshape((-1,)), Reactions_answer),True)

    def test_Main_NonLinearSolve_Disp_Meth_2bars_SnapThrough(self):
        #check that Snap through has occured (cfr J.Feron Master thesis p34 of pdf)
        S0 = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.1], [2.0, 0.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False])
        Loads_To_Apply = np.array([[0.0, 0.0, 0.0], [0.0, 0.0, -15000.0], [0.0, 0.0, 0.0]])

        Elements_A = np.array([0.002500, 0.002500])
        Elements_E = np.array([10000000000.0, 10000000000.0])
        AxialForces_Already_Applied = np.array([])

        S0.test_Main_NonLinearSolve_Displ_Method(100, NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                                 AxialForces_Already_Applied, Loads_To_Apply)
        S1 = StructureObj()
        NodesCoordThrough = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, -0.1], [2.0, 0.0, 0.0]])
        S1.test_Main_NonLinearSolve_Displ_Method(100, NodesCoordThrough, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                                 AxialForces_Already_Applied, Loads_To_Apply)

        last_step0 = S0.Stages.size - 1
        last_step1 = S1.Stages.size - 1

        d0 = S0.Displacements_Results[3*1+2,last_step0] #Solution with snapthrough
        d1 = -0.2+S1.Displacements_Results[3*1+2,last_step1] #Solution starting in tension
        err = 2 / 100  # admissible error
        d_adm = [d1 * (1 + err), d1 * (1 - err)]  # admissible interval
        successD = d0 >= d_adm[0] and d0 <= d_adm[1]
        self.assertEqual(successD, True)


        N0 = S0.AxialForces_Results[0,last_step0] #Solution with snapthrough
        N1 = S1.AxialForces_Results[0,last_step1] #Solution starting in tension
        err = 2 / 100  # admissible error
        N_adm = [N1 * (1 - err), N1 * (1 + err)]  # admissible interval
        successN = N0 >= N_adm[0] and N0 <= N_adm[1]
        self.assertEqual(successN, True)

        minN = S0.AxialForces_Results.min() #Solution with snapthrough
        L0 = S0.Elements_L[0]
        E = S0.ElementsE[0]
        A = S0.ElementsA[0]
        Nsol = E*A*(1-L0)/L0
        err = 2 / 100  # admissible error
        minN_adm = [Nsol * (1 + err), Nsol * (1 - err)]  # admissible interval
        successN = minN >= minN_adm[0] and minN <= minN_adm[1]
        self.assertEqual(successN, True)

        # Reactions_answer = np.array([50000, 0, 50000, 0, -50000, 0, 50000])  # analytique solution
        # self.assertEqual(np.allclose(S0.Reactions_Results, Reactions_answer), True)


    # endregion



    # region Tests on 3 cables \_/ (cfr Luo 2006 - Geometrically NL-FM for assemblies with infinitesimal mechanisms)
    def test_LinearSolve_Force_Method_3cables(self):
        """
        test to check that RegisterData calculates correctly the number of nodes, elements, and supports. Test for 3 cables
        """
        S0 = StructureObj()
        H = 0.080
        L = 3*0.160
        l = L/3 # length of the middle cable
        l1 = np.sqrt(H**2 + l**2) # length of the extreme cables
        cos = l/l1
        sin = H/l1
        NodesCoord = np.array([[0.0,0.0,0.0],[L/3,0.0,-H],[2*L/3,0.0,-H],[L,0.0,0.0]])
        Elements_ExtremitiesIndex = np.array([[0,1],[1,2],[2,3]])
        IsDOFfree = np.array([False,False,False,True,False,True,True,False,True,False,False,False])

        # note that results are independant from EA since statically determinate
        A = 50 # mm²
        E = 70e3 # MPa
        Elements_A = np.array([A,A,A])
        Elements_E = np.array([E,E,E])

        # initial forces. note that results are independant from W since ?
        W = 1000 #N
        t1 = W/sin
        t2 = t1*cos
        Loads_Already_Applied = np.array([[0.0,0.0,0.0],[0.0,0.0,-W],[0.0,0.0,-W],[0.0,0.0,0.0]])
        AxialForces_Already_Applied = np.array([t1,t2,t1])

        # t
        Loads_To_Apply = np.zeros((12,1))
        e = -0.01 # m elongation of the first cable
        Elongations_To_Apply = np.array([e,0,0])

        S0.test_Main_LinearSolve_Force_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                           AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
                                           Elongations_To_Apply)

        Displacements_answer_free = np.array([-5.16,12.04,-5.16,10.32])*1e-3 #analytique solution
        Displacements_answer = np.zeros((12, 1))
        Displacements_answer[IsDOFfree] = Displacements_answer_free.reshape(-1,1)
        self.assertEqual(np.allclose(S0.Displacements_Results,Displacements_answer,atol=1e-5),True)

        S1 = StructureObj()
        e = -0.03  # m elongation of the first cable
        Elongations_To_Apply = np.array([e, 0, 0])

        S1.test_Main_LinearSolve_Force_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                              AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
                                              Elongations_To_Apply)

        Displacements_answer = Displacements_answer * 3
        self.assertEqual(np.allclose(S1.Displacements_Results, Displacements_answer,atol=1e-5), True)

    def test_NonLinearSolve_Force_Method_3cables(self):
        """
        test to check that RegisterData calculates correctly the number of nodes, elements, and supports. Test for 3 cables
        """
        S0 = StructureObj()
        H = 0.080
        L = 3*0.160
        l = L/3 # length of the middle cable
        l1 = np.sqrt(H**2 + l**2) # length of the extreme cables
        cos = l/l1
        sin = H/l1
        NodesCoord = np.array([[0.0,0.0,0.0],[L/3,0.0,-H],[2*L/3,0.0,-H],[L,0.0,0.0]])
        Elements_ExtremitiesIndex = np.array([[0,1],[1,2],[2,3]])
        IsDOFfree = np.array([False,False,False,True,False,True,True,False,True,False,False,False])

        # note that results are independant from EA since statically determinate
        A = 1 # mm²
        E = 1.836e4 # MPa
        Elements_A = np.array([A,A,A])
        Elements_E = np.array([E,E,E])

        # initial forces. note that results are independant from W since ?
        W = 30 #N
        t1 = W/sin
        t2 = t1*cos
        Loads_Already_Applied = np.array([[0.0,0.0,0.0],[0.0,0.0,-W],[0.0,0.0,-W],[0.0,0.0,0.0]])
        AxialForces_Already_Applied = np.array([t1,t2,t1])

        # t
        Loads_To_Apply = np.zeros((12,1))
        e = -0.01 # m elongation of the first cable
        Elongations_To_Apply = np.array([e,0,0])

        S0.test_Main_NonLinearSolve_Force_Method(50,NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                           AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
                                           Elongations_To_Apply)

        Displacements_answer_free = np.array([-5.193,11.809,-5.122,10.090])*1e-3 #from Zhang 2020
        Displacements_answer = np.zeros((12, 1))
        Displacements_answer[IsDOFfree] = Displacements_answer_free.reshape(-1,1)
        self.assertEqual(np.allclose(S0.Displacements_Results,Displacements_answer,atol=1e-5),True)

        S1 = StructureObj()
        e = -0.03  # m elongation of the first cable
        Elongations_To_Apply = np.array([e, 0, 0])

        S1.test_Main_LinearSolve_Force_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                                              AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
                                              Elongations_To_Apply)

        Displacements_answer = Displacements_answer * 3
        self.assertEqual(np.allclose(S1.Displacements_Results, Displacements_answer,atol=1e-5), True)

    # endregion

    # region Tests on 3 cables : force density method
    def test_Force_Density_Method_3cables(self):
        """
        test une méthode de form finding sur un simple example à 3 cables
        """
        S0 = StructureObj()
        H = 1 #m
        L = 4 #m
        l = L/2 # length of the middle cable

        NodesCoord = np.array([[0.0,0.0,0.0],[0.0,0.0,H],[-l,0.0,0.0],[l,0.0,0.0]])
        Elements_ExtremitiesIndex = np.array([[0,1],[0,2],[0,3]])
        IsDOFfree = np.array([True,False,True,False,False,False,False,False,False,False,False,False])

        A = 50.27 # mm²
        E = 70e3 # MPa
        Elements_A = np.array([A,A,A])
        Elements_E = np.array([E,E,E])

        S0.RegisterData(NodesCoord,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E)
        S0.C = S0.Connectivity_Matrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (S0.Elements_L0, S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.NodesCoord, S0.C)

        # (S0.A, S0.A_free, S0.A_fixed) = S0.Compute_Equilibrium_Matrix(S0.Elements_Cos0, S0.C, S0.IsDOFfree)
        t0 = np.array([1, 10, 10])*1000
        q0 = t0/S0.Elements_L0.reshape(-1,)
        Q = np.diag(q0)

        IsXfree = IsDOFfree[0::3]
        IsYfree = IsDOFfree[1::3]
        IsZfree = IsDOFfree[2::3]
        Cx_free = S0.C[:,IsXfree]
        Cy_free = S0.C[:,IsYfree]
        Cz_free = S0.C[:,IsZfree]
        Cx_fix = S0.C[:,~IsXfree]
        Cy_fix = S0.C[:,~IsYfree]
        Cz_fix = S0.C[:,~IsZfree]

        Dx_free = Cx_free.T @ Q @ Cx_free
        Dy_free = Cy_free.T @ Q @ Cy_free
        Dz_free = Cz_free.T @ Q @ Cz_free
        Dx_fix = Cx_free.T @ Q @ Cx_fix
        Dy_fix = Cy_free.T @ Q @ Cy_fix
        Dz_fix = Cz_free.T @ Q @ Cz_fix

        X_fix = S0.NodesCoord.reshape(-1,3)[~IsXfree,0]
        Y_fix = S0.NodesCoord.reshape(-1, 3)[~IsYfree, 1]
        Z_fix = S0.NodesCoord.reshape(-1, 3)[~IsZfree, 2]

        X_free = np.linalg.solve(Dx_free, -Dx_fix @ X_fix)
        Y_free = np.linalg.solve(Dy_free, -Dy_fix @ Y_fix)
        Z_free = np.linalg.solve(Dz_free, -Dz_fix @ Z_fix)

        #UPDATE coordinate
        S1 = StructureObj()
        NodesCoord1 = S0.NodesCoord.copy()
        NodesCoord1.reshape(-1,3)[IsXfree,0] = X_free
        NodesCoord1.reshape(-1, 3)[IsYfree, 1] = Y_free
        NodesCoord1.reshape(-1, 3)[IsZfree, 2] = Z_free

        S1.RegisterData(NodesCoord1,Elements_ExtremitiesIndex,IsDOFfree,Elements_A,Elements_E)
        S1.C = S0.C.copy()#S1.Connectivity_Matrix(S1.NodesCount, S1.ElementsCount, S1.ElementsEndNodes)
        (S1.Elements_L0, S1.Elements_Cos0) = S1.Compute_Elements_Geometry(S1.NodesCoord, S1.C)
        t1 = q0 * S1.Elements_L0

        # Loads_Already_Applied = np.array([[0.0,0.0,0.0],[0.0,0.0,-W],[0.0,0.0,-W],[0.0,0.0,0.0]])
        # AxialForces_Already_Applied = np.array([t1,t2,t1])
        self.assertEqual(False, True)

    # endregion

    # region Tests on 3 cables : Non-linear prestress
    def test_NonLinear_Prestress_3cables(self):
        NodesCoord = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 0.0], [-2.0, 0.0, 0.0], [2.0, 0.0, 0.0]]).reshape(-1,
                                                                                                             1)  # initial nodes coordinates in m
        Elements_ExtremitiesIndex = np.array([[0, 1], [1, 2], [1, 3]])
        d = 8  # diameter in mm
        Area = np.pi * d ** 2 / 4  # area in mm²
        Elements_A = np.array([Area, Area, Area])
        E = 70000  # •Young modulus in MPa
        Elements_E = np.array([E, E, E])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False, False, False, False])

        e = -126.77  # elongation in bar 0 in mm (minus sign for shortening)
        e_To_Apply = np.array([e / 1000, 0, 0])

        S0 = StructureObj()
        S0.RegisterData(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
                        Elongations_To_Apply=e_To_Apply)

        # ITERATION 0 : application of the entire elongation in one step
        S0.Core_Assemble()
        S0.Elements_L0 = S0.Elements_L.copy()
        S0.Elements_Cos0 = S0.Elements_Cos.copy()
        S0.Km = S0.Compute_StiffnessMat_Matrix(S0.A, S0.Elements_L, S0.ElementsA, S0.ElementsE)
        S0.Km_free = S0.Compute_StiffnessMat_Matrix(S0.A_free, S0.Elements_L, S0.ElementsA, S0.ElementsE)
        S0.F = S0.Flexibility_Matrix(S0.ElementsE, S0.ElementsA, S0.Elements_L0)
        # S0.SVD = S0.SVD_Equilibrium_Matrix(S0.A_free)

        # Solve B0.U0 = e_inelastic
        # S0.Displacements_Results = np.linalg.solve(S0.A_free.transpose(),S0.Elongations_To_Apply) # try to solve 3 eq with 2 unknowns raise a LinAlgError because A_free is not square
        S0.Displacements_Results = \
        np.linalg.lstsq(S0.A_free.transpose(), S0.Elongations_To_Apply.reshape(-1), rcond=0.001)[0]

        # Or Solve K.U = f = At = Ake
        t_inelastic = np.linalg.inv(S0.F) @ S0.Elongations_To_Apply
        f_inelastic = S0.A_free @ t_inelastic
        Displacements_Results_free = np.linalg.solve(S0.Km_free, f_inelastic)

        ## ITERATION 1
        # Update
        Displacements_Results = np.zeros(NodesCoord.shape)
        Displacements_Results[IsDOFfree] = Displacements_Results_free
        NodesCoord1 = S0.NodesCoord + Displacements_Results
        S1 = S0.NewStructureObj(NodesCoord1, np.zeros((S0.ElementsCount, 1)), np.zeros((3 * S0.NodesCount, 1)))
        S1.Elongations_To_Apply = S0.Elongations_To_Apply.copy()

        # Compute Equilibrium matrix
        (S1.Elements_L, S1.Elements_Cos) = S1.Compute_Elements_Geometry(S1.NodesCoord,
                                                                        S1.C)  # cos = (X2_def - X1_def)/L_def
        (S1.A, S1.A_free, S1.A_fixed) = S1.Compute_Equilibrium_Matrix(S1.Elements_Cos, S1.C, S1.IsDOFfree)

        # find e_elastic = B1@U0
        e_elastic = S1.A_free.transpose() @ Displacements_Results_free  # A_free contient les cos dans la position déformée avec les longueurs déformées
        e_tot = e_elastic - S1.Elongations_To_Apply

        # find total forces
        L_def_approx = S0.Elements_L0.reshape(-1, 1) + S0.Elongations_To_Apply
        S1.F = S1.Flexibility_Matrix(S1.ElementsE, S1.ElementsA, L_def_approx.reshape(-1, ))
        k1_bsc = np.linalg.inv(S1.F)
        t_tot = k1_bsc @ e_tot

        f_unbalanced = -(S1.A_free @ t_tot)  # unbalanced = external load - resisting forces (external load = 0)
        S1.Km_free = S1.A_free @ k1_bsc @ (S1.A_free.transpose())
        Displacements1_Results_free = np.linalg.solve(S1.Km_free, f_unbalanced)

        ## ITERATION 2
        # Update
        Displacements1_Results = np.zeros(NodesCoord.shape)
        Displacements1_Results[IsDOFfree] = Displacements1_Results_free
        NodesCoord2 = S1.NodesCoord + Displacements1_Results
        S2 = S1.NewStructureObj(NodesCoord2, np.zeros((S0.ElementsCount, 1)), np.zeros((3 * S0.NodesCount, 1)))

        # Compute Equilibrium matrix
        (S2.Elements_L, S2.Elements_Cos) = S2.Compute_Elements_Geometry(S2.NodesCoord,
                                                                        S2.C)  # cos = (X2_def - X1_def)/L_def
        (S2.A, S2.A_free, S2.A_fixed) = S2.Compute_Equilibrium_Matrix(S2.Elements_Cos, S2.C, S2.IsDOFfree)

        # find e_elastic = B1@U0
        e2_elastic = S2.A_free.transpose() @ Displacements1_Results_free  # A_free contient les cos dans la position déformée avec les longueurs déformées
        e2_tot = e2_elastic

        # find total forces
        # L_def_approx = S0.Elements_L0.reshape(-1,1)+S0.Elongations_To_Apply
        # S2.F = S2.Flexibility_Matrix(S2.ElementsE, S2.ElementsA, L_def_approx.reshape(-1,))
        # k2_bsc = np.linalg.inv(S2.F)
        t2_tot = k1_bsc @ e2_tot

        f2_unbalanced = -(S2.A_free @ t2_tot)  # unbalanced = external load - resisting forces (external load = 0)
        S2.Km_free = S2.A_free @ k1_bsc @ (S2.A_free.transpose())
        Displacements2_Results_free = np.linalg.solve(S2.Km_free, f2_unbalanced)
    # endregion

if __name__ == '__main__':
    unittest.main()