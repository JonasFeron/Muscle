# -*- coding: utf-8 -*-
import unittest
from StructureObj import *
import numpy as np
import scipy.linalg as lin
import scipy.optimize as opt


class StructureObj_Tests(unittest.TestCase):




    # region Assemble methods

    def test_Simple_ConnectivityMatrix(self):
        """
        test to see if the computation of the connectivity_matrix of 2 cables (*--c1--*--c2--*) works
        """
        S0 = StructureObj() #empty object

        #required input for the method
        ElementsCount = 2
        NodesCount = 3
        ElementsEndNodes = np.array([[0,1],[1,2]])

        C = S0.ConnectivityMatrix(NodesCount, ElementsCount, ElementsEndNodes)  #test the method

        #check the results
        success = (C == np.array([[-1,  1,  0],[ 0, -1, 1]])).all()
        self.assertEqual(success, True)


    def test_CompareMaterialStiffnessMatricesFromTwoMethods(self):
        Struct = StructureObj()
        NodesCoord = np.array([[-1.0, 0.0, 0.0], [0.0, 0.0, 2.0], [1.0, 0.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, False, True, False, False, False])
        ElementsType = np.array([-1, -1]) #two struts
        ElementsE = np.array([[70, 70],
                              [70, 70]]) * 1e3  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1]]) * 100 # mm²

        Struct.InitialData(NodesCoord,ElementsEndNodes,IsDOFfree,ElementsType,ElementsA,ElementsE)

        ini = Struct.Initial
        #0) For linear calculation, compute the elements propeteries according to their types.
        ini.ElementsE = Struct.ElementsInTensionOrCompression(Struct.ElementsType, Struct.ElementsE) #select the young modulus EinCompression for struts or EinTension for cables
        ini.ElementsA = Struct.ElementsInTensionOrCompression(Struct.ElementsType, Struct.ElementsA)

        #1) Compute the material stiffness matrix by the method 1, from a list of local stiffness matrices
        (ini.ElementsL, ini.ElementsCos) = ini.ElementsLengthsAndCos(Struct, ini.NodesCoord)
        kmLocList = ini.MaterialLocalStiffnessList(Struct, ini.ElementsL, ini.ElementsCos, ini.ElementsA, ini.ElementsE)
        Kmat1 = ini.GlobalStiffnessMatrix(Struct,kmLocList)

        #2) Compute the material stiffness matrix by the method 2, from the equilibrium matrix
        (ini.A, ini.AFree, ini.AFixed) = ini.EquilibriumMatrix(Struct, ini.ElementsCos)
        ini.Flex = Struct.Flexibility(ini.ElementsE, ini.ElementsA,ini.ElementsL)
        Kmat2 = ini.MaterialStiffnessMatrix(Struct,ini.A,ini.Flex)

        successKmat = np.allclose(Kmat1,Kmat2)
        self.assertEqual(successKmat, True)

    # endregion
    # region Linear Displacement Method

    def test_MainLinearDisplacementMethod_2bars(self):
        #Simple tests on 2 bars /\ (cfr Annexe A1.1.1 of J.Feron Master thesis (p103 of pdf))
        Struct = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 1.0],
                               [2.0, 0.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])
        LoadsToApply = np.array([[0.0, 0.0, 0.0],
                                   [0.0, 0.0, -100000],
                                   [0.0, 0.0, 0.0]])
        ElementsType = np.array([-1,-1])
        ElementsA = np.array([0.002500, 0.002500])
        ElementsE = np.array([10000000000, 10000000000])


        Struct.test_MainLinearDisplacementMethod( NodesCoord, ElementsEndNodes, IsDOFfree,ElementsType, ElementsA,ElementsE,LoadsToApply=LoadsToApply)

        displacements = Struct.Final.NodesCoord-Struct.Initial.NodesCoord
        d1Z = displacements.reshape((-1, 3))[1, 2]
        SuccessD = np.isclose(d1Z ,-5.6568 * 1e-3, atol=1e-6)

        self.assertEqual(SuccessD, True)

        Forces_answer = np.array([-70711, -70711])  # analytique solution
        self.assertEqual(np.allclose(Struct.Final.Tension, Forces_answer), True)

        Reactions_answer = np.array([50000, 0, 50000, 0, -50000, 0, 50000])  # analytique solution
        self.assertEqual(np.allclose(Struct.Final.Reactions, Reactions_answer), True)

    def test_MainLinearDisplacementMethod_Prestress2cables(self):
        #Simple prestress tests on a tight rope
        Struct = StructureObj()
        NodesCoord = np.array([[-2.0, 0.0, 0.0],
                               [0.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0],
                               [0.0, 0.0, 1.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2],
                                     [1, 3]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False,
                              False, False, False])
        LoadsToApply = np.array([[0.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0],
                                 [0.0, 0.0, 0.0],
                                    [0.0, 0.0, 0.0]])
        ElementsType = np.array([1,1,1])
        ElementsA = np.array([1, 1, 1]) * 50.26 #[mm²]
        ElementsE = np.array([70, 70, 70])*1e3 #[MPa]

        LenghteningsToApply = np.array([-0.007984,0,0]) #[m]

        ini = Struct.Initial

        Struct.test_MainLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree,ElementsType, ElementsA,ElementsE,LoadsToApply=LoadsToApply,LengtheningsToApply=LenghteningsToApply)

        displacements = Struct.Final.NodesCoord-Struct.Initial.NodesCoord
        d1X = displacements.reshape((-1, 3))[1, 0]
        SuccessD = np.isclose(d1X ,-4 * 1e-3, rtol=1e-2)

        self.assertEqual(SuccessD, True)

        t = Struct.Final.Tension
        t_answer = np.array([7037.17, 7037.17,0])  # analytique solution
        self.assertEqual(np.allclose(t[:1], t_answer[:1],rtol=1e-2), True)

    # endregion

    # region NONLinear Displacement Method

    def test_MainNONLinearDisplacementMethod_2bars(self):
        # Simple tests on 2 bars /\ (cfr Annexe A1.1.1 of J.Feron Master thesis (p103 of pdf))
        Struct = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 1.0],
                               [2.0, 0.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])
        LoadsToApply = np.array([[0.0, 0.0, 0.0],
                                 [0.0, 0.0, -100000],
                                 [0.0, 0.0, 0.0]])
        ElementsType = np.array([-1, -1])
        ElementsA = np.array([0.002500, 0.002500])
        ElementsE = np.array([10000000000, 10000000000])


        Struct.test_MainNONLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                 ElementsE, LoadsToApply=LoadsToApply,n_steps=100)

        displacements = Struct.Final.NodesCoord - Struct.Initial.NodesCoord
        d1Z = displacements.reshape((-1, 3))[1, 2]
        SuccessD = np.isclose(d1Z, -5.6568 * 1e-3, rtol=1e-2)

        self.assertEqual(SuccessD, True)

        Forces_answer = np.array([-70711, -70711])  # analytique solution
        self.assertEqual(np.allclose(Struct.Final.Tension, Forces_answer,rtol=1e-2), True)

    def test_MainNONLinearDisplacementMethod_2bars_SnapThrough(self):
        #check that Snap through has occured (cfr J.Feron Master thesis p34 of pdf)
        Struct = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 0.1],
                               [2.0, 0.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])
        LoadsToApply = np.array([[0.0, 0.0, 0.0],
                                 [0.0, 0.0, -15],
                                 [0.0, 0.0, 0.0]])*1e3
        ElementsType = np.array([-1, -1])
        ElementsA = np.array([2500, 2500])
        ElementsE = np.array([1, 1])*10000

        Struct.test_MainNONLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                    ElementsE, LoadsToApply=LoadsToApply, n_steps=100)


        StructReversed = StructureObj()
        NodesCoordReversed = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, -0.1],
                               [2.0, 0.0, 0.0]])

        StructReversed.test_MainNONLinearDisplacementMethod(NodesCoordReversed, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                    ElementsE, LoadsToApply=LoadsToApply, n_steps=100)

        self.assertEqual(np.allclose(Struct.Final.Tension, StructReversed.Final.Tension, rtol=2e-2), True)
        self.assertEqual(np.allclose(Struct.Final.NodesCoord, StructReversed.Final.NodesCoord, rtol=2e-2), True)



    def test_MainNONLinearDisplacementMethod_Prestress2cables(self):
        # Simple prestress tests on a tight rope
        Struct = StructureObj()
        NodesCoord = np.array([[-2.0, 0.0, 0.0],
                               [0.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0],
                               [0.0, 0.0, 1.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2],
                                     [1, 3]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False,
                              False, False, False])
        LoadsToApply = np.array([[0.0, 0.0, 0.0],
                                 [0.0, 0.0, 0.0],
                                 [0.0, 0.0, 0.0],
                                 [0.0, 0.0, 0.0]])
        ElementsType = np.array([1, 1, 1])
        ElementsA = np.array([1, 1, 1]) * 50.26  # [mm²]
        ElementsE = np.array([70, 70, 70]) * 1e3  # [MPa]

        LenghteningsToApply = np.array([-0.007984, 0, 0])  # [m]

        ini = Struct.Initial

        Struct.test_MainNONLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                 ElementsE, LoadsToApply=LoadsToApply,
                                                 LengtheningsToApply=LenghteningsToApply,n_steps=100)

        displacements = Struct.Final.NodesCoord - Struct.Initial.NodesCoord
        d1X = displacements.reshape((-1, 3))[1, 0]
        SuccessD = np.isclose(d1X, -4 * 1e-3, rtol=1e-2)

        self.assertEqual(SuccessD, True)

        t = Struct.Final.Tension
        t_answer = np.array([7037.17, 7037.17, 0])  # analytique solution
        self.assertEqual(np.allclose(t[:1], t_answer[:1], rtol=1e-2), True)

    def test_SimpleB_MainNONLinearDisplacementMethod(self):
        """
        A simple benchmark test B with 3 cables.
        :return:
        """

        Struct = StructureObj()

        NodesCoord = np.array([[2.0, 0.0, 1.0],
                               [0.0, 0.0, 0.0],
                               [4.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              False, False, False,
                              False, False, False,
                              True, False, True])

        ElementsEndNodes = np.array([[0, 3],
                                     [1, 3],
                                     [2, 3]])
        ElementsType = np.array([1,1,1])

        ElementsE = np.array([[70, 70],
                              [70, 70],
                              [70, 70]]) * 1e3  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1],
                              [1, 1]]) * 50.26  # mm²
        LengtheningsToApply = np.array([-126.775,
                                        0,
                                        0])*1e-3 #m
        LoadsToApply = np.array([[0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0]])
        #Let's try the method when initial Lfree is unknown and we want to calculate a lengtheningtoapply

        Struct.test_MainNONLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE, LoadsToApply=LoadsToApply,LengtheningsToApply=LengtheningsToApply, n_steps=100)

        TensionAnalyticAnswer = np.array([888.81,
                                         7037.17,
                                         7037.17]) #N
        NodesCoordAnalyticAnswer = np.array([[2.0, 0.0, 1.0],
                                             [0.0, 0.0, 0.0],
                                             [4.0, 0.0, 0.0],
                                             [2.0, 0.0, 0.126554]]).reshape((-1,))
        successForces = np.isclose(Struct.Final.Tension,TensionAnalyticAnswer,rtol=3e-2) #relative tolérance of 1/1000
        successNodes = np.isclose(Struct.Final.NodesCoord,NodesCoordAnalyticAnswer,rtol=1e-2)

        self.assertEqual(successForces.all(), True)
        self.assertEqual(successNodes.all(), True)

    def test_MainNONLinearDisplacementMethod_LoadsOnTightRope(self):
        #cfr master thesis Jferon

        Struct = StructureObj()

        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])

        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        ElementsType = np.array([1, 1])

        ElementsE = np.array([[1, 1],
                              [1, 1]]) * 10000  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1]]) * 2500  # mm²
        LengtheningsToApply = np.array([0, 0]) * 1e-3  # m
        LoadsToApply = np.array([[0, 0, 0],
                                 [0, 0, -100000.0],
                                 [0, 0, 0]]) #m

        Struct.test_MainNONLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                    ElementsE, LoadsToApply=LoadsToApply,
                                                    LengtheningsToApply=LengtheningsToApply, n_steps=100)

        TensionAnalyticAnswer = np.array([313020,
                                          313020])  # N
        NodesCoordAnalyticAnswer = np.array([[0.0, 0.0, 0.0],
                                             [1.0, 0.0, -158.74*1e-3],
                                             [2.0, 0.0, 0.0]]).reshape((-1,))
        successForces = np.isclose(Struct.Final.Tension, TensionAnalyticAnswer, rtol=2e-2)  # relative tolérance of 1/1000
        successNodes = np.isclose(Struct.Final.NodesCoord, NodesCoordAnalyticAnswer, rtol=2e-2)

        self.assertEqual(successForces.all(), True)
        self.assertEqual(successNodes.all(), True)

    def test_MainNONLinearDisplacementMethod_TightRope_3stages(self):
        #cfr solution in excel files attached

        ### STAGE PRESTRESS
        S0 = StructureObj()

        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])

        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        ElementsType = np.array([1, 1])

        ElementsE = np.array([[1, 1],
                              [1, 1]]) * 100000  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1]]) * 50  # mm²

        LengtheningsToApply = np.array([-3.984, -3.984]) * 1e-3  # m


        S0.test_MainNONLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                    ElementsE,LengtheningsToApply=LengtheningsToApply, n_steps=100)

        PrestressForcesResult= np.array([20000, 20000])# N
        successForces = np.isclose(S0.Final.Tension, PrestressForcesResult,rtol=2e-2)
        self.assertEqual(successForces.all(), True)

        ### STAGE FIRST LOAD
        S1 = StructureObj()
        LoadsToApply1 = np.array([[0, 0, 0],
                                 [0, 0, -5109.0],
                                 [0, 0, 0]])  # N

        S1.test_MainNONLinearDisplacementMethod(S0.Final.NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                ElementsE, ElementsLFreeInit=S0.Final.ElementsLFree, LoadsToApply=LoadsToApply1,
                                                TensionInit=S0.Final.Tension,ReactionsInit=S0.Final.Reactions, n_steps=100)

        d_sol1 = -75.0 * 1e-3  # analytique solution
        t_sol1 = 34043 # analytique solution

        successForces1 = np.isclose(S1.Final.Tension, np.array([t_sol1,t_sol1]),rtol=2e-2)
        self.assertEqual(successForces1.all(), True)

        d1 = S1.Final.NodesCoord-S0.Initial.NodesCoord
        successDispl1 = np.isclose(d1.reshape(-1,3)[1,2], d_sol1,rtol=2e-2)
        self.assertEqual(successDispl1.all(), True)


        ### STAGE SECOND LOAD
        S2 = StructureObj()
        LoadsToApply2 = np.array([[0, 0, 0],
                                 [0, 0, -9988.0],
                                 [0, 0, 0]])  # N

        AdditionalLoads = LoadsToApply2-LoadsToApply1

        S2.test_MainNONLinearDisplacementMethod(S1.Final.NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                ElementsE, ElementsLFreeInit=S0.Final.ElementsLFree, LoadsToApply=AdditionalLoads,
                                                LoadsInit=S1.Final.Loads, TensionInit=S1.Final.Tension, ReactionsInit=S1.Final.Reactions, n_steps=100)

        d_sol2 = -105.0 * 1e-3  # analytique solution
        t_sol2 = 47487 # analytique solution

        successForces2 = np.isclose(S2.Final.Tension, np.array([t_sol2,t_sol2]),rtol=2e-2)
        self.assertEqual(successForces2.all(), True)

        d2 = S2.Final.NodesCoord-S0.Initial.NodesCoord
        successDispl2 = np.isclose(d2.reshape(-1,3)[1,2], d_sol2,rtol=2e-2)
        self.assertEqual(successDispl2.all(),True)

    # endregion

    # region Dynamic Relaxation Method
    def test_Simplest_MainDynamicRelaxation(self):
        """
        A simple benchmark test with 2 cables oscillating around the equilibrium position with a little bit of prestress.
        :return:
        """

        Struct = StructureObj()

        NodesCoord = np.array([[-2.0, 0.0, 0.0],
                               [0.0, 0.0, 0.1], # lets pull the free node in the direction of the mechanism as a starting point
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])
        ElementsType = np.array([1, 1])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        ElementsE = np.array([[70, 70],
                              [70, 70]]) * 1e3  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1]]) * 50.26  # mm²
        ElementsLFree = np.array([1.999,  #-126.775
                                  1.999]) # m
        LengtheningsToApply = np.array([0,  #-126.775
                                        0])*1e-3 #m
        LoadsToApply = np.array([[0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0]])
        Dt = 0.01
        Struct.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE,
                                          ElementsLFree, None, None, None, LoadsToApply, LengtheningsToApply, Dt=Dt)

        success = np.isclose(Struct.Final.Tension,70000*50.26*0.001/1.999*np.ones(2,),rtol=1e-2)

        self.assertEqual(success.all(), True)

    def test_SimpleB_MainDynamicRelaxation(self):
        """
        A simple benchmark test B with 3 cables.
        :return:
        """

        Struct = StructureObj()

        NodesCoord = np.array([[2.0, 0.0, 1.0],
                               [0.0, 0.0, 0.0],
                               [4.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              False, False, False,
                              False, False, False,
                              True, True, True])
        ElementsType = np.array([1, 1,1])
        ElementsEndNodes = np.array([[0, 3],
                                     [1, 3],
                                     [2, 3]])
        ElementsE = np.array([[70, 70],
                              [70, 70],
                              [70, 70]]) * 1e3  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1],
                              [1, 1]]) * 50.26  # mm²
        LengtheningsToApply = np.array([-126.775,
                                        0,
                                        0])*1e-3 #m
        LoadsToApply = np.array([[0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0]])
        #Let's try the method when initial Lfree is unknown and we want to calculate a lengtheningtoapply

        Dt = 0.01
        Struct.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE, None,
                                          None, None, None, LoadsToApply, LengtheningsToApply, Dt=Dt)

        TensionAnalyticAnswer = np.array([888.81,
                                         7037.17,
                                         7037.17]) #N
        NodesCoordAnalyticAnswer = np.array([[2.0, 0.0, 1.0],
                                             [0.0, 0.0, 0.0],
                                             [4.0, 0.0, 0.0],
                                             [2.0, 0.0, 0.126554]]).reshape((-1,))
        successForces = np.isclose(Struct.Final.Tension,TensionAnalyticAnswer,rtol=1e-3) #relative tolérance of 1/1000
        successNodes = np.isclose(Struct.Final.NodesCoord,NodesCoordAnalyticAnswer,atol=1e-6)

        self.assertEqual(successForces.all(), True)
        self.assertEqual(successNodes.all(), True)

    def test_SimpleC_MainDynamicRelaxation(self):
        """
        A simple benchmark test with 3 cables and with reorientation of the shortening axis
        :return:
        """

        Struct = StructureObj()

        NodesCoord = np.array([[0.0, 0.0, 1.0],
                               [0.0, 0.0, 0.0],
                               [4.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              False, False, False,
                              False, False, False,
                              True, True, True])
        ElementsType = np.array([1, 1,1])
        ElementsEndNodes = np.array([[0, 3],
                                     [1, 3],
                                     [2, 3]])
        ElementsE = np.array([[70, 70],  # let's say cable 0 can only be in tension
                              [70, 70],
                              [70, 70]]) * 1e3  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1],
                              [1, 1]]) * np.pi *(8/2)**2  # mm²
        LengtheningsToApply = np.array([-52.110,
                                        0,
                                        0])*1e-3 #m
        LoadsToApply = np.array([[0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0]])
        #Let's try the method when initial Lfree is unknown and we want to calculate a lengtheningtoapply

        Dt = 0.01
        Struct.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE, None,
                                          None, None, None, LoadsToApply, LengtheningsToApply,
                                          Residual0Threshold=0.00001, Dt=Dt)


        TensionAnalyticAnswer = np.array([1823.48,
                                         5365.62,
                                         7037.17]) #N
        NodesCoordAnalyticAnswer = np.array([[0.0, 0.0, 1.0],
                                             [0.0, 0.0, 0.0],
                                             [4.0, 0.0, 0.0],
                                             [2.0-0.000476, 0.0, 0.118795]]).reshape((-1,))
        successForces = np.isclose(Struct.Final.Tension,TensionAnalyticAnswer,rtol=1e-3) #relative tolérance of 1/1000
        successNodes = np.isclose(Struct.Final.NodesCoord,NodesCoordAnalyticAnswer,atol=1e-6)

        self.assertEqual(successForces.all(), True)
        self.assertEqual(successNodes.all(), True)

    def test_SimpleCslack_MainDynamicRelaxation(self):
        """
        A simple benchmark test with 3 cables and slack cables
        :return:
        """

        Struct = StructureObj()

        NodesCoord = np.array([[0.0, 0.0, 1.0],
                               [0.0, 0.0, 0.0],
                               [4.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              False, False, False,
                              False, False, False,
                              True, True, True])
        ElementsType = np.array([1, 1,1])
        ElementsEndNodes = np.array([[0, 3],
                                     [1, 3],
                                     [2, 3]])
        ElementsE = np.array([[0, 70],  # let's say cable 0 can only be in tension
                              [70, 70],
                              [70, 70]]) * 1e3  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1],
                              [1, 1]]) * 50.26  # mm²
        LengtheningsToApply = np.array([0,
                                        -7.984,
                                        0])*1e-3 #m
        LoadsToApply = np.array([[0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0],
                                 [0, 0, 0]])
        #Let's try the method when initial Lfree is unknown and we want to calculate a lengtheningtoapply

        Dt = 0.01
        Struct.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE, None,
                                          None, None, None, LoadsToApply, LengtheningsToApply, Dt=Dt)


        TensionAnalyticAnswer = np.array([0,
                                         7037.17,
                                         7037.17]) #N
        NodesCoordAnalyticAnswer = np.array([[0.0, 0.0, 1.0],
                                             [0.0, 0.0, 0.0],
                                             [4.0, 0.0, 0.0],
                                             [2.0-0.004000, 0.0, 0.0]]).reshape((-1,))
        successForces = np.isclose(Struct.Final.Tension,TensionAnalyticAnswer,rtol=1e-3) #relative tolérance of 1/1000
        successNodes = np.isclose(Struct.Final.NodesCoord,NodesCoordAnalyticAnswer,atol=1e-6)

        self.assertEqual(successForces.all(), True)
        self.assertEqual(successNodes.all(), True)

    def test_Simplex_MainDynamicRelaxation(self):
        """
        Compare the results of this DR method with the results of Landolf Rhode Barbarigos for the case of the experimental simplex with the shortening of one horizontal cable
        :return:
        """

        Struct = StructureObj()

        NodesCoord = np.array([[   0.00, -2043.82, 0.00],
                               [   0.00,     0.00, 0.00],
                               [1770.00, -1021.91, 0.00],
                               [ 590.00, -2201.91, 1950.00],
                               [-431.91,  -431.91, 1950.00],
                               [1611.91,  -431.91, 1950.00]])*1e-3
        IsDOFfree = np.array([False, True, False,
                              False, False, False,
                              True, True, False,
                              True, True, True,
                              True, True, True,
                              True, True, True])
        ElementsType = np.array([-1, -1,-1,1,1,1,1,1,1,1,1,1])
        ElementsEndNodes = np.array([[2, 4],
                                     [1, 3],
                                     [0, 5],
                                     [1, 2],
                                     [0, 1],
                                     [0, 2],
                                     [4, 5],
                                     [3, 4],
                                     [3, 5],
                                     [2, 5],
                                     [1, 4],
                                     [0, 3]])

        #Bars can only be in compression and cables only in tension
        ElementsE = np.array([[70390, 0],
                              [70390, 0],
                              [70390, 0],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750]])  # MPa
        ElementsA = np.ones((12,2))
        ElementsA[0:3,:] = 364.4
        ElementsA[3:12,:] = 50.3

        ElementsLFree = np.array([2999.8,
    2999.8,
    2999.8,
    2043.8,
    2043.8,
    2043.8,
    2043.8,
    2043.8,
    2043.8,
    2043.4,
    2043.4,
    2043.4])*1e-3


        LengtheningsToApply = np.zeros((12,)) #m
        LengtheningsToApply[0:3] = 0.835*1e-3
        LengtheningsToApply[8] = -35 * 1e-3

        LoadsToApply = np.zeros((6,3))
        LoadsToApply[0:3,2] = 45.7
        LoadsToApply[3:6,2] = 41.6 #N

        Dt = 0.01
        Struct.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree,ElementsType, ElementsA, ElementsE,
                                          ElementsLFree, None, None, None, LoadsToApply, LengtheningsToApply,
                                          Residual0Threshold=0.00001, Dt=Dt)

        TensionDRMatlabAnswer = np.array([-9848.26151894298,
        -9882.41664832343,
        -9874.50280077890,
        3953.87930064950,
        3835.52819661200,
        3808.51599478652,
        3859.21359327111,
        3858.16975358279,
        3947.80984861979,
        6653.65253640084,
        6677.35302197632,
        6744.48294062936]) #N

        NodesCoordDRMatlabAnswer = np.array([[   0.00, -2045.97206933403, 0.00],
                               [   0.00,     0.00, 0.00],
                               [1771.89364968302, - 1023.06835531595, 0.00],
                               [ 616.024764975095, - 2197.43254689303, 1946.45254155930],
                               [-427.528116330227,  - 437.602999235727, 1953.63046329029],
                               [1618.37958793442,  - 454.066751469362, 1960.50103999593]]).reshape((-1,))*1e-3
        successForces = np.isclose(Struct.Final.Tension,TensionDRMatlabAnswer,rtol=1e-2) #relative tolérance of 5/1000
        successNodes = np.isclose(Struct.Final.NodesCoord,NodesCoordDRMatlabAnswer,rtol=1e-2)

        self.assertEqual(successForces.all(), True)
        self.assertEqual(successNodes.all(), True)



    def test_MainDynamicRelaxation_TightRope_3stages(self):
        #cfr solution in excel files attached

        ### STAGE PRESTRESS
        S0 = StructureObj()

        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])

        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        ElementsType = np.array([1, 1])

        ElementsE = np.array([[1, 1],
                              [1, 1]]) * 100000  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1]]) * 50  # mm²

        LengtheningsToApply = np.array([-3.984, -3.984]) * 1e-3  # m


        S0.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                    ElementsE,LengtheningsToApply=LengtheningsToApply, Dt=0.1)

        PrestressForcesResult= np.array([20000, 20000])# N
        successForces = np.isclose(S0.Final.Tension, PrestressForcesResult,rtol=2e-2)
        self.assertEqual(successForces.all(), True)

        ### STAGE FIRST LOAD
        S1 = StructureObj()
        LoadsToApply1 = np.array([[0, 0, 0],
                                 [0, 0, -5109.0],
                                 [0, 0, 0]])  # N

        S1.test_MainDynamicRelaxation(S0.Final.NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                ElementsE, ElementsLFreeInit=S0.Final.ElementsLFree, LoadsToApply=LoadsToApply1,
                                                TensionInit=S0.Final.Tension,ReactionsInit=S0.Final.Reactions, Dt=0.1)

        d_sol1 = -75.0 * 1e-3  # analytique solution
        t_sol1 = 34043 # analytique solution

        successForces1 = np.isclose(S1.Final.Tension, np.array([t_sol1,t_sol1]),rtol=2e-2)
        self.assertEqual(successForces1.all(), True)

        d1 = S1.Final.NodesCoord-S0.Initial.NodesCoord
        successDispl1 = np.isclose(d1.reshape(-1,3)[1,2], d_sol1,rtol=2e-2)
        self.assertEqual(successDispl1.all(), True)


        ### STAGE SECOND LOAD
        S2 = StructureObj()
        LoadsToApply2 = np.array([[0, 0, 0],
                                 [0, 0, -9988.0],
                                 [0, 0, 0]])  # N

        AdditionalLoads = LoadsToApply2-LoadsToApply1

        S2.test_MainDynamicRelaxation(S1.Final.NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                ElementsE, ElementsLFreeInit=S0.Final.ElementsLFree, LoadsToApply=AdditionalLoads,
                                                LoadsInit=S1.Final.Loads, TensionInit=S1.Final.Tension, ReactionsInit=S1.Final.Reactions, Dt=0.1)

        d_sol2 = -105.0 * 1e-3  # analytique solution
        t_sol2 = 47487 # analytique solution

        successForces2 = np.isclose(S2.Final.Tension, np.array([t_sol2,t_sol2]),rtol=2e-2)
        self.assertEqual(successForces2.all(), True)

        d2 = S2.Final.NodesCoord-S0.Initial.NodesCoord
        successDispl2 = np.isclose(d2.reshape(-1,3)[1,2], d_sol2,rtol=2e-2)
        self.assertEqual(successDispl2.all(),True)

    def test_MainDynamicRelaxation_TightRope_3stages_Reversed(self):
        #cfr solution in excel files attached

        ### STAGE PRESTRESS
        S0 = StructureObj()

        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])

        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        ElementsType = np.array([1, 1])

        ElementsE = np.array([[1, 1],
                              [1, 1]]) * 100000  # MPa
        ElementsA = np.array([[1, 1],
                              [1, 1]]) * 50  # mm²


        LoadsToApply1 = np.array([[0, 0, 0],
                                 [0, 0, -5109.0],
                                 [0, 0, 0]])  # N

        S0.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                    ElementsE,LoadsToApply=LoadsToApply1, Dt=0.1)

        # PrestressForcesResult= np.array([20000, 20000])# N
        # successForces = np.isclose(S0.Final.Tension, PrestressForcesResult,rtol=2e-2)
        # self.assertEqual(successForces.all(), True)

        ### STAGE FIRST LOAD
        S1 = StructureObj()

        LengtheningsToApply = np.array([-3.984, -3.984]) * 1e-3  # m
        S1.test_MainDynamicRelaxation(S0.Final.NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                ElementsE, ElementsLFreeInit=S0.Final.ElementsLFree, LengtheningsToApply=LengtheningsToApply,
                                                LoadsInit=S0.Final.Loads,TensionInit=S0.Final.Tension,ReactionsInit=S0.Final.Reactions, Dt=0.1)

        d_sol1 = -75.0 * 1e-3  # analytique solution
        t_sol1 = 34043 # analytique solution

        successForces1 = np.isclose(S1.Final.Tension, np.array([t_sol1,t_sol1]),rtol=2e-2)
        self.assertEqual(successForces1.all(), True)

        d1 = S1.Final.NodesCoord-S0.Initial.NodesCoord
        successDispl1 = np.isclose(d1.reshape(-1,3)[1,2], d_sol1,rtol=2e-2)
        self.assertEqual(successDispl1.all(), True)


        ### STAGE SECOND LOAD
        S2 = StructureObj()
        LoadsToApply2 = np.array([[0, 0, 0],
                                 [0, 0, -9988.0],
                                 [0, 0, 0]])  # N

        AdditionalLoads = LoadsToApply2-LoadsToApply1

        S2.test_MainDynamicRelaxation(S1.Final.NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                ElementsE, ElementsLFreeInit=S1.Final.ElementsLFree, LoadsToApply=AdditionalLoads,
                                                LoadsInit=S1.Final.Loads, TensionInit=S1.Final.Tension, ReactionsInit=S1.Final.Reactions, Dt=0.1)

        d_sol2 = -105.0 * 1e-3  # analytique solution
        t_sol2 = 47487 # analytique solution

        successForces2 = np.isclose(S2.Final.Tension, np.array([t_sol2,t_sol2]),rtol=2e-2)
        self.assertEqual(successForces2.all(), True)

        d2 = S2.Final.NodesCoord-S0.Initial.NodesCoord
        successDispl2 = np.isclose(d2.reshape(-1,3)[1,2], d_sol2,rtol=2e-2)
        self.assertEqual(successDispl2.all(),True)
    # endregion

    # region FORCE Methods



    def test_Simplex_SensitivityMatrix(self):
        """
        Find the sensitivity matrix of the experimental simplex

        :return:
        """


        #ref :  [1] Kwan, Pellegrino, 1993, Prestressing a Space Structure
        # [2] Xue, Y. et al. (2021) “Comparison of different sensitivity matrices relating element elongations to structural response of pin-jointed structures,” Mechanics Research Communications. Elsevier Ltd, 118(May), p. 103789. doi: 10.1016/j.mechrescom.2021.103789.

        Struct = StructureObj()

        NodesCoord = np.array([[   0.00, -2043.82, 0.00],
                               [   0.00,     0.00, 0.00],
                               [1770.00, -1021.91, 0.00],
                               [ 590.00, -2201.91, 1950.00],
                               [-431.91,  -431.91, 1950.00],
                               [1611.91,  -431.91, 1950.00]])*1e-3
        IsDOFfree = np.array([False, True, False,
                              False, False, False,
                              True, True, False,
                              True, True, True,
                              True, True, True,
                              True, True, True])
        ElementsType = np.array([-1, -1,-1,1,1,1,1,1,1,1,1,1])
        ElementsEndNodes = np.array([[2, 4],
                                     [1, 3],
                                     [0, 5],
                                     [1, 2],
                                     [0, 1],
                                     [0, 2],
                                     [4, 5],
                                     [3, 4],
                                     [3, 5],
                                     [2, 5],
                                     [1, 4],
                                     [0, 3]])

        #Bars can only be in compression and cables only in tension
        ElementsE = np.array([[70390, 0],
                              [70390, 0],
                              [70390, 0],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 72190],
                              [0, 72190],
                              [0, 72190]])  # MPa
        # ElementsE = np.array([[70390, 0],
        #                       [70390, 0],
        #                       [70390, 0],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860]])  # MPa
        ElementsA = np.ones((12,2))
        ElementsA[0:3,:] = 364.4
        ElementsA[3:12,:] = 50.3
        # ElementsA[3:12,:] = 0


        # ElementsLFree = np.array([2999.8,
        #                           2999.8,
        #                           2999.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.4,
        #                           2043.4,
        #                           2043.4])*1e-3

        Struct = StructureObj()

        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)


        # Struct.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        # Struct.Initial.ElementsE = Struct.ElementsInTensionOrCompression(ElementsType,ElementsE)
        # Struct.Initial.ElementsA = Struct.ElementsInTensionOrCompression(ElementsType, ElementsA)
        #
        # (l, ElementsCos) = Struct.Initial.ElementsLengthsAndCos(Struct, NodesCoord)
        # (A, AFree, AFixed) = Struct.Initial.EquilibriumMatrix(Struct, ElementsCos)
        # Struct.Initial.SVD.SVDEquilibriumMatrix(Struct, AFree)
        #
        # #S = Struct.Initial.SVD.Vs_row.T #Self-stress matrix
        # S = Struct.Initial.SVD.SS.T  # Self-stress matrix
        # Struct.Initial.Flex = Struct.Flexibility(Struct.Initial.ElementsE, Struct.Initial.ElementsA, l)
        # F = np.diag(Struct.Initial.Flex)
        # Ke = np.diag(1/Struct.Initial.Flex)
        #
        # a = 1500 # prestress level [N]
        # t0 = S * a # prestress forces [N] # assumption no self-weight
        # q = Struct.Initial.ForceDensities(t0, l) #
        # kgLocList = Struct.Initial.GeometricLocalStiffnessList(Struct, q)
        # Kgeo = Struct.LocalToGlobalStiffnessMatrix(kgLocList)
        # KgeoFree = Kgeo[Struct.IsDOFfree].T[Struct.IsDOFfree].T
        #
        # BFree = AFree.T # the compatibility matrix
        #
        # #According to [1] and [2]
        # SFS = S.T @ F @ S # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        # Ks = np.linalg.inv(SFS)
        # Sa = -Ks @ S.T # Sensitivity of the prestress level to a given elongation
        # St1 = S @ Sa # Sensitivity of the tensions to a given elongation
        # Se1 = F @ St1 # Sensitivity of the elastic elongations to a given imposed elongation
        #
        # B__ = np.linalg.pinv(BFree) #the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        # Sd1 = B__ @ (Se1 + np.eye(Struct.ElementsCount)) #Sensitivity of the displacements to a given imposed elongation, assuming the elongation do not activate the mechanism.
        #
        # # According to [1]
        # Kmat = AFree @ Ke @ BFree
        # Kmat__ = np.linalg.pinv(Kmat)
        # Sd2 = Kmat__ @ AFree @ Ke #equivalent to Sd1
        # St2 = Ke @ BFree @ Sd2 - Ke #equivalent to St1
        # SD2 = np.around(Sd2.reshape((1,-1)),4)
        #
        # # According to [1]
        #
        # Ktan__ = np.linalg.inv(Kmat+KgeoFree)
        # Sd3 = Ktan__ @ AFree @ Ke
        # St3 = Ke @ BFree @ Sd3 - Ke
        # CT3 = Sd3[:,8]

        self.assertEqual(False, True)



    def test_2Simplex_SensitivityMatrix(self):
        """
        Find the sensitivity matrix of the two experimental simplex superimposed

        :return:
        """

        # ref :  [1] Kwan, Pellegrino, 1993, Prestressing a Space Structure
        # [2] Xue, Y. et al. (2021) “Comparison of different sensitivity matrices relating element elongations to structural response of pin-jointed structures,” Mechanics Research Communications. Elsevier Ltd, 118(May), p. 103789. doi: 10.1016/j.mechrescom.2021.103789.

        Struct = StructureObj()

        NodesCoord = np.array([[0.00, -2043.82, 0.00],
                               [0.00, 0.00, 0.00],
                               [1770.00, -1021.91, 0.00],
                               [590.00, -2201.91, 1950.00],
                               [-431.91, -431.91, 1950.00],
                               [1611.91, -431.91, 1950.00],
                               [1180.00, -2043.82, 3900.00],
                               [-590.00, -1021.91, 3900.00],
                               [1180.00, 0.00, 3900.00]]) * 1e-3

        IsDOFfree = np.array([False, True, False,
                              False, False, False,
                              True, True, False,
                              True, True, True,
                              True, True, True,
                              True, True, True,
                              True, True, True,
                              True, True, True,
                              True, True, True])
        ElementsType = np.array([-1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1, -1, -1, -1, 1, 1, 1, 1, 1, 1])
        ElementsEndNodes1 = np.array([[2, 4],
                                      [1, 3],
                                      [0, 5],
                                      [1, 2],
                                      [0, 1],
                                      [0, 2],
                                      [4, 5],
                                      [3, 4],
                                      [3, 5],
                                      [2, 5],
                                      [1, 4],
                                      [0, 3]])
        ElementsEndNodesTemp = ElementsEndNodes1 + 3  # il faut retirer les câbles de bases en commun entre les 2 simplex
        ElementsEndNodes2 = np.delete(ElementsEndNodesTemp, [3, 4, 5], 0)

        ElementsEndNodes = np.vstack((ElementsEndNodes1, ElementsEndNodes2))

        # Bars can only be in compression and cables only in tension
        ElementsE1 = np.array([[70390, 0],
                               [70390, 0],
                               [70390, 0],
                               [0, 71750],
                               [0, 71750],
                               [0, 71750],
                               [0, 71750],
                               [0, 71750],
                               [0, 71750],
                               [0, 71750],
                               [0, 71750],
                               [0, 71750]])  # MPa

        ElementsE = np.vstack((ElementsE1, np.delete(ElementsE1, [3, 4, 5], 0)))

        # ElementsE = np.array([[70390, 0],
        #                       [70390, 0],
        #                       [70390, 0],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860],
        #                       [0, 2860]])  # MPa
        ElementsA1 = np.ones((12, 2))
        ElementsA1[0:3, :] = 364.4
        ElementsA1[3:12, :] = 50.3
        ElementsA = np.vstack((ElementsA1, np.delete(ElementsA1, [3, 4, 5], 0)))

        # ElementsLFree = np.array([2999.8,
        #                           2999.8,
        #                           2999.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.8,
        #                           2043.4,
        #                           2043.4,
        #                           2043.4])*1e-3

        Struct = StructureObj()
        Struct.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        Struct.Initial.ElementsE = Struct.ElementsInTensionOrCompression(ElementsType, ElementsE)
        Struct.Initial.ElementsA = Struct.ElementsInTensionOrCompression(ElementsType, ElementsA)

        (l, ElementsCos) = Struct.Initial.ElementsLengthsAndCos(Struct, NodesCoord)
        (A, AFree, AFixed) = Struct.Initial.EquilibriumMatrix(Struct, ElementsCos)
        Struct.Initial.SVD.SVDEquilibriumMatrix(Struct, AFree)
        # S = Struct.Initial.SVD.Vs_row.T #Self-stress matrix
        S = Struct.Initial.SVD.SS.T  # Self-stress matrix
        S = np.array([
            [-1, 0],  # bottom struts
            [-1, 0],
            [-1, 0],
            [0.39335503, 0],  # bottom horizontal cables
            [0.39335503, 0],
            [0.39335503, 0],
            [0.39335503, 0.39335503],  # middle horizontal cables shared between both simplex
            [0.39335503, 0.39335503],
            [0.39335503, 0.39335503],
            [0.68117977, 0],  # bottom vertical cables
            [0.68117977, 0],
            [0.68117977, 0],
            [0, -1],  # top struts
            [0, -1],
            [0, -1],
            [0, 0.39335503],  # top horizontal cables
            [0, 0.39335503],
            [0, 0.39335503],
            [0, 0.68117977],  # top vertical cables
            [0, 0.68117977],
            [0, 0.68117977]])

        Struct.Initial.Flex = Struct.Flexibility(Struct.Initial.ElementsE, Struct.Initial.ElementsA, l)
        F = np.diag(Struct.Initial.Flex)
        Ke = np.diag(1 / Struct.Initial.Flex)

        a = np.array([1500, 1500])  # prestress levels [N]
        t0 = S @ a  # prestress forces [N] # assumption no self-weight
        q = Struct.Initial.ForceDensities(t0, l)  #
        kgLocList = Struct.Initial.GeometricLocalStiffnessList(Struct, q)
        Kgeo = Struct.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Struct.IsDOFfree].T[Struct.IsDOFfree].T

        BFree = AFree.T  # the compatibility matrix

        # According to [1] and [2]
        SFS = S.T @ F @ S  # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        Ks = np.linalg.inv(SFS)
        Sa = -Ks @ S.T  # Sensitivity of the prestress level to a given elongation
        St1 = S @ Sa  # Sensitivity of the tensions to a given elongation
        Se1 = F @ St1  # Sensitivity of the elastic elongations to a given imposed elongation

        B__ = np.linalg.pinv(
            BFree)  # the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        Sd1 = B__ @ (Se1 + np.eye(
            Struct.ElementsCount))  # Sensitivity of the displacements to a given imposed elongation, assuming the elongation do not activate the mechanism.

        # According to [1]
        Kmat = AFree @ Ke @ BFree
        Kmat__ = np.linalg.pinv(Kmat)
        Sd2 = Kmat__ @ AFree @ Ke  # equivalent to Sd1
        St2 = Ke @ BFree @ Sd2 - Ke  # equivalent to St1

        # According to [1]

        Ktan__ = np.linalg.inv(Kmat + KgeoFree)
        Sd3 = Ktan__ @ AFree @ Ke
        St3 = Ke @ BFree @ Sd3 - Ke
        CT3 = Sd3[:, 8]

        self.assertEqual(False, True)


    def test_2Simplex_SortSelfStressModes(self):
        """
        Find the independant self-stress modes of the two experimental simplex superimposed

        :return:
        """


        #ref :  [1] Kwan, Pellegrino, 1993, Prestressing a Space Structure
        # [2] Xue, Y. et al. (2021) “Comparison of different sensitivity matrices relating element elongations to structural response of pin-jointed structures,” Mechanics Research Communications. Elsevier Ltd, 118(May), p. 103789. doi: 10.1016/j.mechrescom.2021.103789.

        Struct = StructureObj()

        NodesCoord = np.array([[   0.00, -2043.82, 0.00],
                               [   0.00,     0.00, 0.00],
                               [1770.00, -1021.91, 0.00],
                               [ 590.00, -2201.91, 1950.00],
                               [-431.91,  -431.91, 1950.00],
                               [1611.91,  -431.91, 1950.00],
                               [1180.00, -2043.82, 3900.00],
                               [-590.00, -1021.91, 3900.00],
                               [1180.00,     0.00, 3900.00]])*1e-3


        IsDOFfree = np.array([False, True, False,
                              False, False, False,
                              True, True, False,
                              True, True, True,
                              True, True, True,
                              True, True, True,
                              True, True, True,
                              True, True, True,
                              True, True, True])
        ElementsType = np.array([-1, -1,-1,1,1,1,1,1,1,1,1,1,-1,-1,-1,1,1,1,1,1,1])
        ElementsEndNodes1 = np.array([[2, 4],
                                     [1, 3],
                                     [0, 5],
                                     [1, 2],
                                     [0, 1],
                                     [0, 2],
                                     [4, 5],
                                     [3, 4],
                                     [3, 5],
                                     [2, 5],
                                     [1, 4],
                                     [0, 3]])
        ElementsEndNodesTemp = ElementsEndNodes1+3 #il faut retirer les câbles de bases en commun entre les 2 simplex
        ElementsEndNodes2 = np.delete(ElementsEndNodesTemp, [3,4,5], 0)

        ElementsEndNodes = np.vstack((ElementsEndNodes1,ElementsEndNodes2))

        #Bars can only be in compression and cables only in tension
        ElementsE1 = np.array([[70390, 0],
                              [70390, 0],
                              [70390, 0],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750],
                              [0, 71750]])  # MPa

        ElementsE = np.vstack((ElementsE1,np.delete(ElementsE1, [3,4,5], 0)))


        ElementsA1 = np.ones((12,2))
        ElementsA1[0:3,:] = 364.4
        ElementsA1[3:12,:] = 50.3
        ElementsA = np.vstack((ElementsA1, np.delete(ElementsA1, [3,4,5], 0)))


        Struct = StructureObj()
        Struct.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        Struct.Initial.ElementsE = Struct.ElementsInTensionOrCompression(ElementsType,ElementsE)
        Struct.Initial.ElementsA = Struct.ElementsInTensionOrCompression(ElementsType, ElementsA)
        (Struct.Initial.ElementsL, Struct.Initial.ElementsCos) = Struct.Initial.ElementsLengthsAndCos(Struct, NodesCoord)
        (A, AFree, AFixed) = Struct.Initial.EquilibriumMatrix(Struct, Struct.Initial.ElementsCos)
        Struct.Initial.SVD.SVDEquilibriumMatrix(Struct, AFree)
        Vs = Struct.Initial.SVD.Vs_row.T #Self-stress matrix
        SS = Struct.Initial.SVD.SS.T  # Self-stress matrix

        SS_sol = np.array([
            [-1, 0],#bottom struts
            [-1, 0],
            [-1, 0],
            [0.39335503, 0],#bottom horizontal cables
            [0.39335503, 0],
            [0.39335503, 0],
            [0.39335503, 0.39335503],  # middle horizontal cables shared between both simplex
            [0.39335503, 0.39335503],
            [0.39335503, 0.39335503],
            [0.68117977, 0],  # bottom vertical cables
            [0.68117977, 0],
            [0.68117977, 0],
            [0, -1], #top struts
            [0, -1],
            [0, -1],
            [0, 0.39335503],#top horizontal cables
            [0, 0.39335503],
            [0, 0.39335503],
            [0, 0.68117977],  # top vertical cables
            [0, 0.68117977],
            [0, 0.68117977]])

        CheckMode0 = np.logical_or(np.isclose(SS[:,0],SS_sol[:,0],atol=1e-6),np.isclose(SS[:,0],SS_sol[:,1],atol=1e-6))
        CheckMode1 = np.logical_or(np.isclose(SS[:,1],SS_sol[:,0],atol=1e-6),np.isclose(SS[:,1],SS_sol[:,1],atol=1e-6))
        Check = np.logical_and(CheckMode0,CheckMode1).all()

        self.assertEqual(Check, True)

    def test_3Simplex_SortSelfStressModes(self):
        """
        Find the independant self-stress modes of the three experimental simplex

        :return:
        """


        #ref :  [1] Kwan, Pellegrino, 1993, Prestressing a Space Structure
        # [2] Xue, Y. et al. (2021) “Comparison of different sensitivity matrices relating element elongations to structural response of pin-jointed structures,” Mechanics Research Communications. Elsevier Ltd, 118(May), p. 103789. doi: 10.1016/j.mechrescom.2021.103789.

        Struct = StructureObj()

        NodesCoord = np.array([[0.0, -2.04381998, 0.0],
                               [0.0, -2E-08, 0.0],
                               [1.77, -1.02191, 0.0],
                               [0.59000026, -2.20191, 1.95],
                               [-0.43191011, -0.43191023, 1.95],
                               [1.61190984, -0.43190977, 1.95],
                               [0.0, -2.04381998, 3.9],
                               [0.0, -2E-08, 3.9],
                               [1.77, -1.02191, 3.9],
                               [0.59000026, -2.20191, 5.85],
                               [-0.43191011, -0.43191023, 5.85],
                               [1.61190984, -0.43190977, 5.85]])


        IsDOFfree = np.array([False,True,False,False,False,False,True,True,False,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True,True])
        ElementsEndNodes = np.array([[2, 4], [1, 3], [0, 5], [5, 6], [4, 8], [3, 7], [8, 10], [7, 9], [6, 11], [2, 1], [1, 0],
                             [0, 2], [5, 4], [4, 3], [3, 5], [8, 7], [7, 6], [6, 8], [11, 10], [10, 9], [9, 11], [2, 5],
                             [1, 4], [0, 3], [5, 8], [4, 7], [3, 6], [8, 11], [7, 10], [6, 9]])


        ElementsType = np.array([-1,-1,-1,-1,-1,-1,-1,-1,-1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1])

        #Bars can only be in compression and cables only in tension
        ElementsA = np.array([[364.42475,364.42475],[364.42475,364.42475],[364.42475,364.42475],[364.42475,364.42475],[364.42475,364.42475],[364.42475,364.42475],[364.42475,364.42475],[364.42475,364.42475],[364.42475,364.42475],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548],[50.26548,50.26548]])  # MPa


        ElementsE = np.array([[70390.0,70390.0],[70390.0,70390.0],[70390.0,70390.0],[70390.0,70390.0],[70390.0,70390.0],[70390.0,70390.0],[70390.0,70390.0],[70390.0,70390.0],[70390.0,70390.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[71750.0,71750.0],[72190.0,72190.0],[72190.0,72190.0],[72190.0,72190.0],[72190.0,72190.0],[72190.0,72190.0],[72190.0,72190.0],[72190.0,72190.0],[72190.0,72190.0],[72190.0,72190.0]])


        Struct = StructureObj()
        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)


        self.assertEqual(True, True)


    def test_2XSnelson_SortSelfStressModes(self):
        """
        Find the independant self-stress modes of the three X Snelson modules

        :return:
        """


        #ref :  [1] Kwan, Pellegrino, 1993, Prestressing a Space Structure
        # [2] Xue, Y. et al. (2021) “Comparison of different sensitivity matrices relating element elongations to structural response of pin-jointed structures,” Mechanics Research Communications. Elsevier Ltd, 118(May), p. 103789. doi: 10.1016/j.mechrescom.2021.103789.

        Struct = StructureObj()

        NodesCoord = np.array([[ 0, 0, 0],
                               [ 2, 0, 0],
                               [ 4, 0, 0],
                               [ 0, 0, 2],
                               [ 2, 0, 2],
                               [ 4, 0, 2]])


        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False,
                              True, False, True,
                              True, False, True,
                              True, False, True])
        ElementsEndNodes = np.array([[1, 3],
                                     [0, 4],
                                     [2, 4],
                                     [1, 5],
                                     [0, 1],
                                     [3, 4],
                                     [1, 2],
                                     [4, 5],
                                     [0, 3],
                                     [1, 4],
                                     [2, 5]])
        ElementsType = np.array([-1, -1, -1, -1, 1, 1, 1, 1, 1, 1, 1])

        #Bars can only be in compression and cables only in tension
        ElementsE = np.array([[1, 0],
                               [1, 0],
                               [1, 0],
                               [1, 0],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1]])*70000  # MPa


        ElementsA = np.ones((11,2)) * 50.3
        ElementsA[[0,1,2,3],:] = 364.4


        Struct = StructureObj()
        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        SS = Struct.Initial.SVD.SS
        e0 = np.zeros((11,)) #lengtheningToApply
        e0[8] = -1
        e0mod = -SS@e0
        self.assertEqual(False, True)

    def test_3XSnelson_SortSelfStressModes(self):
        """
        Find the independant self-stress modes of the three X Snelson modules

        :return:
        """


        #ref :  [1] Kwan, Pellegrino, 1993, Prestressing a Space Structure
        # [2] Xue, Y. et al. (2021) “Comparison of different sensitivity matrices relating element elongations to structural response of pin-jointed structures,” Mechanics Research Communications. Elsevier Ltd, 118(May), p. 103789. doi: 10.1016/j.mechrescom.2021.103789.

        Struct = StructureObj()

        NodesCoord = np.array([[ 0, 0, 0],
                               [ 2, 0, 0],
                               [ 4, 0, 0],
                               [ 6, 0, 0],
                               [ 0, 0, 2],
                               [ 2, 0, 2],
                               [ 4, 0, 2],
                               [ 6, 0, 2]])


        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              True, False, True,
                              False, False, False,
                              True, False, True,
                              True, False, True,
                              True, False, True,
                              True, False, True])
        ElementsEndNodes = np.array([[1, 4],
                                     [0, 5],
                                     [0, 1],
                                     [0, 4],
                                     [4, 5],
                                     [1, 5],
                                     [2, 5],
                                     [1, 6],
                                     [3, 6],
                                     [2, 7],
                                     [1, 2],
                                     [2, 3],
                                     [5, 6],
                                     [6, 7],
                                     [2, 6],
                                     [3, 7]])
        ElementsType = np.array([-1, -1, 1, 1, 1, 1, -1, -1, -1, -1, 1, 1, 1, 1, 1, 1])

        #Bars can only be in compression and cables only in tension
        ElementsE = np.array([[1, 0],
                               [1, 0],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [1, 0],
                               [1, 0],
                               [1, 0],
                               [1, 0],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1],
                               [0, 1]])*70000  # MPa


        ElementsA = np.ones((16,2)) * 50.3
        ElementsA[[0,1,6,7,8,9],:] = 364.4


        Struct = StructureObj()
        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        # Struct.Initial.ElementsE = Struct.ElementsInTensionOrCompression(ElementsType,ElementsE)
        # Struct.Initial.ElementsA = Struct.ElementsInTensionOrCompression(ElementsType, ElementsA)
        # (Struct.Initial.ElementsL, Struct.Initial.ElementsCos) = Struct.Initial.ElementsLengthsAndCos(Struct, NodesCoord)
        # (A, AFree, AFixed) = Struct.Initial.EquilibriumMatrix(Struct, Struct.Initial.ElementsCos)
        # Struct.Initial.SVD.SVDEquilibriumMatrix(Struct, AFree)
        # Vs = Struct.Initial.SVD.Vs_row.T #Self-stress matrix
        # SS = Struct.Initial.SVD.SS.T  # Self-stress matrix

        self.assertEqual(True, True)

    def test_SelfStressModesStiffness_2XSnelson_paper(self):
        """

        :return:
        """


        #ref :  [1] Aloui, O., Lin, J., Rhode-Barbarigos, L. (2019). A theoretical framework for sensor placement, structural identification and damage detection in tensegrity structures. Smart Materials and Structures,


        Struct = StructureObj()

        NodesCoord = np.array([[ 0, 0, 0],
                               [ 1, 0, -0.2],
                               [ 0.8, 0, 0.8],
                               [ -0.2, 0, 1],
                               [ 2.2, 0, 1],
                               [ 2, 0, 0]]) # n = 6


        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              True, False, True,
                              True, False, True,
                              True, False, True,
                              True, False, False]) # ndof = 9 degrees of freedom
        ElementsEndNodes = np.array([[1, 2],
                                     [2, 3],
                                     [3, 4],
                                     [1, 4],
                                     [1, 3],
                                     [2, 4],
                                     [3, 5],
                                     [5, 6],
                                     [2, 6],
                                     [2, 5],
                                     [3, 6]])
        ElementsEndNodes -= 1 #nodes index start at 0 not at 1 in python

        ElementsType = np.ones((11,))  # b = 11 elements
        ElementsType[[4, 5, 9, 10]] = -1 #struts

        #Bars can only be in compression and cables only in tension
        ElementsE = np.ones((11,2)) * 70000 # MPa


        ElementsA = np.ones((11,2)) * 50
        ElementsA[[4,5,9,10],:] = 365


        Struct = StructureObj()
        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)

        #Structure's data
        F = np.diag(Struct.Initial.Flex*1e6) #flexibility matrix - size (b,b) - mm/kN
        K = np.linalg.inv(F) #element stiffness matrix - size (b,b) - kN/mm
        A = Struct.Initial.AFree #equilibrium matrix - size (ndof,b) - (no unit)
        s = Struct.Initial.SVD.s #degree of static indeterminacy - scalar - (no unit)

        L = Struct.Initial.ElementsL*1000 #assembled lengths - size (b,) - mm

        #Self-stress modes given by SVD (Pellegrino, 1993)
        Vs = Struct.Initial.SVD.Vs_row.T # modes - size (b,s) - (no unit)
        Vs_squared = Vs.T @ Vs  # equal to [I] therefore Vs is orthonormal

        #Localized Self-stress modes After transformation (with Sanchez 2007).
        S = Struct.Initial.SVD.SS.T  #localized modes - size (b,s) - (no unit)
        #L_inv = np.diag(1/Struct.Initial.ElementsL)
        #q_S = L_inv @ S # if one want to compute forces densities
        #Zero_check1 = A @ S # if = 0 : the mode is in self-equilibrium : test_succeeded
        S_squared = S.T @ S #different than [I] therefore S is not orthonormal
        Theta = Vs.T @ S #transformation matrix from Vs to S


        #Forces sensitivity matrices :
        SMt_Vs = -Vs @ np.linalg.inv(Vs.T @ F @ Vs) @ Vs.T #size (b,b) - (kN/mm)
        SMt_S = -S @ np.linalg.inv(S.T @ F @ S) @ S.T #size (b,b) - (kN/mm)
        #Conclusion : SMt_Vs = SMt_S


        #Stiffness K_S of localized self-stress modes S :
        K_S = np.linalg.inv(S.T @ F @ S) #stiffness - size (s,s) - (kN/mm)
        F_S = S.T @ F @ S # flexibility - size (s,s) - (mm/kN)
        SMa = -K_S @ S.T # levels sensitivity matrix - size (s,b) - (kN/mm)


        ####   targeted forces   ####
        #1) apply unit external load
        LoadsToApply = np.zeros((6,3))
        LoadsToApply[2,2] = -1   # load - N - applied on node 3 in -Z direction
        Struct.test_MainLinearDisplacementMethod(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                 ElementsE, LoadsToApply=LoadsToApply)
        #2) counter balance compression in cables with prestress forces
        forces_from_loads = Struct.Final.Tension *10
        #Zero_check2 = A @ forces_from_loads # if = 0 : the load is in equilibrium with the internal forces: test_succeeded
        target_levels = np.array([2.05, 4.1])
        target_state = S @ target_levels
        total_forces = forces_from_loads + target_state
        Modal_scenarios = F_S @ target_levels

        #choice of elements equipped with devices
        selected_devices = np.array([2, 10]) - 1
        S_row_devices = S[selected_devices, :].T
        Prestress_scenario = np.linalg.solve(-S_row_devices, Modal_scenarios)


        #Self-stress scenario
        Ks_diag = np.diag(np.diag(K_S))
        Kappa = K_S @ np.linalg.inv(Ks_diag)
        SelfStressScenario = - F @ target_state

        SelfStressScenario_mod2 = - F @ S @ np.array([0, 4.1])
        t_mod2 = S @ np.array([0, 4.1])

        # CURRENT self-stress levels / state identification
        loads = Struct.LoadsToApply[IsDOFfree] * 10

        Sensors_ind = np.array([1,3,7,9])-1 #position of the force sensors
        #t_meas = np.array([0.6009,1.15560,0.63627]) #force measured by the sensors
        t_tot_meas = np.array([5.6,0.5,1.5,6.9]) #force measured by the sensors
        A__ = np.linalg.pinv(A) #pseudo inverse of A
        A__sensors = A__[Sensors_ind]
        tf_known = A__sensors @ loads
        t_known = t_tot_meas - tf_known

        S_sensors = S[Sensors_ind] #forces in the sensors in each self-stress mode
        SS_sensors = np.hstack((S_sensors,S_sensors))
        SS_sensors_inv = np.linalg.pinv(SS_sensors)
        af_a = SS_sensors_inv @ t_tot_meas  # self-stress levels


        t_identified = S @ tss


        Kss = Struct.Initial.SVD.Ks/1e6
        SMa = Kss @ S.T
        SMt = S @ SMa


        tss_sensitivity = -Kss_diag@S.T
        tss = np.array([6.67,6.78])
        ess = np.linalg.solve(Kss,tss)
        SelfStressScenario = - F @ S @ tss
        t = S @ tss


        # Struct.Initial.ElementsE = Struct.ElementsInTensionOrCompression(ElementsType,ElementsE)
        # Struct.Initial.ElementsA = Struct.ElementsInTensionOrCompression(ElementsType, ElementsA)
        # (Struct.Initial.ElementsL, Struct.Initial.ElementsCos) = Struct.Initial.ElementsLengthsAndCos(Struct, NodesCoord)
        # (A, AFree, AFixed) = Struct.Initial.EquilibriumMatrix(Struct, Struct.Initial.ElementsCos)
        # Struct.Initial.SVD.SVDEquilibriumMatrix(Struct, AFree)
        # Vs = Struct.Initial.SVD.Vs_row.T #Self-stress matrix
        # S = Struct.Initial.SVD.S.T  # Self-stress matrix

        self.assertEqual(True, True)

    def test_SelfStressModesStiffness_4modules_paper(self):
        """

        :return:
        """


        #ref :  [1] Aloui, O., Lin, J., Rhode-Barbarigos, L. (2019). A theoretical framework for sensor placement, structural identification and damage detection in tensegrity structures. Smart Materials and Structures,


        Struct = StructureObj()

        NodesCoord = np.array([[ 0, 0, 0],
                               [ 1, 0, -0.2],
                               [ 0.8, 0, 0.8],
                               [ -0.2, 0, 1],
                               [ 2.2, 0, 1],
                               [ 2, 0, 0],
                               [ 0, 0, 2],
                               [ 1, 0, 2.2],
                               [ 2, 0, 2]])


        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              True, False, True,
                              True, False, True,
                              True, False, True,
                              True, False, False,
                              True, False, True,
                              True, False, True,
                              True, False, True])
        ElementsEndNodes = np.array([[1, 2],
                                     [2, 3],
                                     [3, 4],
                                     [1, 4],
                                     [1, 3],
                                     [2, 4],
                                     [3, 5],
                                     [5, 6],
                                     [2, 6],
                                     [2, 5],
                                     [3, 6],
                                     [4, 7],
                                     [7, 8],
                                     [3, 8],
                                     [3, 7],
                                     [4, 8],
                                     [5, 8],
                                     [5, 9],
                                     [3, 9],
                                     [8, 9]])
        ElementsEndNodes -= 1 #nodes index start at 0 not at 1.

        ElementsType = np.ones((20,))
        ElementsType[[4, 5, 9, 10, 14, 15, 16, 18]] = -1

        #Bars can only be in compression and cables only in tension
        ElementsE = np.ones((20,2)) * 70000 # MPa


        ElementsA = np.ones((20,2)) * 50
        ElementsA[[4,5,9,10,14,15,16,18],:] = 365


        Struct = StructureObj()
        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)

        s = Struct.Initial.SVD.s
        S = Struct.Initial.SVD.SS.T  # Self-stress matrix:
        shape = S.shape
        # reorganizing method of the self-stress modes do not work
        #according to ref 1 :
        qs = np.zeros(shape) #self-stress modes in terms of force density in N/m
        qs[[0,1,2,3,4,5],0] = [1,1,1,1,-1,-1] #mode 0
        qs[[1,6,7,8,9,10],1] = [1,0.764,1.147,1.5,-1.083,-1.058] #mode 1
        qs[[2,11,12,13,14,15],2] = [1,1.5,1.147,0.764,-1.058,-1.083] #mode 2
        qs[[6,13,16,17,18,19],3] = [1,1,-1.5,2,-1.333,2] #mode 3
        qs[[1,2,5,6,9,13,15,16],4] = [-1,-1,0.5,-0.5,0.333,-0.5,0.333,0.25]   #mode 4

        L = np.diag(Struct.Initial.ElementsL)
        S_ref_Barbarigos = L@qs #self-stress modes in terms of forces in N
        S = np.zeros(shape)
        for i in range(s):
            mode = S_ref_Barbarigos.T[i]
            CompressionMax = mode.min()
            TensionMax = mode.max()
            bool = -CompressionMax > TensionMax  # true if |compression max| > tension max
            max = np.where(bool, CompressionMax, TensionMax)
            S.T[i] = -mode/max # self-stress modes Matrix. we made sure the max value is always equal to -1 in compression whatever the mode

        S[:,4] *= -1


        #Structure's data
        F = np.diag(Struct.Initial.Flex*1e6) #flexibility matrix - size (b,b) - mm/kN
        K = np.linalg.inv(F) #element stiffness matrix - size (b,b) - kN/mm
        A = Struct.Initial.AFree #equilibrium matrix - size (ndof,b) - (no unit)
        s = Struct.Initial.SVD.s #degree of static indeterminacy - scalar - (no unit)
        L = Struct.Initial.ElementsL*1000 #assembled lengths - size (b,) - mm

        A_FDM = A @ np.diag(L)
        U_FDM, S_FDM, V_FDM_row = np.linalg.svd(A_FDM)
        U_check, S_check, V_check_row = np.linalg.svd(A)

        Zero_check = A @ S

        #Forces sensitivity matrices :
        SMt_S = -S @ np.linalg.inv(S.T @ F @ S) @ S.T #size (b,b) - (kN/mm)
        Vs = Struct.Initial.SVD.Vs_row.T
        SMt_Vs = -Vs @ np.linalg.inv(Vs.T @ F @ Vs) @ Vs.T #size (b,b) - (kN/mm)


        #Conclusion : SMt_Vs = SMt_S

        #Stiffness K_S of localized self-stress modes S :
        K_S = np.linalg.inv(S.T @ F @ S) #stiffness - size (s,s) - (kN/mm)
        F_S = S.T @ F @ S # flexibility - size (s,s) - (mm/kN)
        SMa = -K_S @ S.T # levels sensitivity matrix - size (s,b) - (kN/mm)

        ####   targeted forces in the final structure  ####

        target_levels = np.array([5.0, 5.0, 5.0, 5.0, 1.0])
        target_state = S @ target_levels
        SelfStressScenario = - F @ target_state
        Modal_scenarios = F_S @ target_levels
        Ks_diag = np.diag(np.diag(K_S))
        Kappa = K_S @ np.linalg.inv(Ks_diag)


        # Independant Self-stress scenarios
        target_level_1 = np.array([5, 0, 0, 0, 0])
        SelfStressScenario_1 = - F @ S @ target_level_1
        #check_target_1 = SMa@SelfStressScenario_1

        target_level_2 = np.array([0, 5, 0, 0, 0])
        SelfStressScenario_2 = - F @ S @ target_level_2

        target_level_3 = np.array([0, 0, 5, 0, 0])
        SelfStressScenario_3 = - F @ S @ target_level_3

        target_level_4 = np.array([0, 0, 0, 5, 0])
        SelfStressScenario_4 = - F @ S @ target_level_4

        target_level_5 = np.array([0, 0, 0, 0, 1])
        SelfStressScenario_5 = - F @ S @ target_level_5


        ####   THEORETICAL CONSTRUCTION  ####


        ####   stage 1 - module 1 ####

        # Structure's data
        SelectElements = np.arange(6) #build elements 0 to 5
        imposed_elongation_1 = SelfStressScenario[SelectElements]

        F1 = np.diag(Struct.Initial.Flex[SelectElements]*1e6)  # element flexibility matrix - size (b,b) - kN/mm

        S1 = S[SelectElements, 0].reshape((-1,1))

        # Stiffness K_S of localized self-stress modes S :
        F_S1 = S1.T @ F1 @ S1  # flexibility - size (s,s) - (mm/kN)
        K_S1 = np.linalg.inv(F_S1)  # stiffness - size (s,s) - (kN/mm)
        Ks_diag1 = np.diag(np.diag(K_S1))
        Kappa1 = K_S1 @ np.linalg.inv(Ks_diag1)

        EPS_1 = - S1.T @ imposed_elongation_1 # modal scenario - size (s,) - (mm)
        a_1 = K_S1 @ EPS_1
        t_1 = S1 @ a_1
        e_1 = F1 @ t_1


        ####   stage 2 - module 2 ####

        # Structure's data
        SelectElements = np.arange(11) #build elements 0 to 10
        imposed_elongation_2 = SelfStressScenario[SelectElements]

        F2 = np.diag(Struct.Initial.Flex[SelectElements]*1e6)  # element flexibility matrix - size (b,b) - kN/mm
        S2 = S[SelectElements,0:2]

        # Stiffness K_S of localized self-stress modes S :
        F_S2 = S2.T @ F2 @ S2  # flexibility - size (s,s) - (mm/kN)
        K_S2 = np.linalg.inv(F_S2)  # stiffness - size (s,s) - (kN/mm)
        Ks_diag2 = np.diag(np.diag(K_S2))
        Kappa2 = K_S2 @ np.linalg.inv(Ks_diag2)

        EPS_2 = - S2.T @ imposed_elongation_2 # modal scenario - size (s,) - (mm)
        a_2 = K_S2 @ EPS_2
        t_2 = S2 @ a_2
        e_2 = F2 @ t_2

        ####   stage 3 - module 3 ####

        # Structure's data
        SelectElements = np.arange(16) #build elements 0 to 16
        imposed_elongation_3 = SelfStressScenario[SelectElements]

        F3 = np.diag(Struct.Initial.Flex[SelectElements]*1e6)  # element flexibility matrix - size (b,b) - kN/mm
        S3 = S[SelectElements,0:3]

        # Stiffness K_S of localized self-stress modes S :
        F_S3 = S3.T @ F3 @ S3  # flexibility - size (s,s) - (mm/kN)
        K_S3 = np.linalg.inv(F_S3)  # stiffness - size (s,s) - (kN/mm)
        Ks_diag3 = np.diag(np.diag(K_S3))
        Kappa3 = K_S3 @ np.linalg.inv(Ks_diag3)

        EPS_3 = - S3.T @ imposed_elongation_3 # modal scenario - size (s,) - (mm)
        a_3 = K_S3 @ EPS_3
        t_3 = S3 @ a_3
        e_3 = F3 @ t_3


        ####   4 stage - mode 5 ####

        # Structure's data
        SelectElements = np.arange(17)  # build elements 0 to 16
        imposed_elongation_4 = SelfStressScenario[SelectElements]

        F4 = np.diag(Struct.Initial.Flex[SelectElements] * 1e6)  # element flexibility matrix - size (b,b) - kN/mm
        SelectModes = np.array([0,1,2,4])
        S4 = S[SelectElements,:][:,SelectModes]

        # Stiffness K_S of localized self-stress modes S :
        F_S4 = S4.T @ F4 @ S4  # flexibility - size (s,s) - (mm/kN)
        K_S4 = np.linalg.inv(F_S4)  # stiffness - size (s,s) - (kN/mm)
        Ks_diag4 = np.diag(np.diag(K_S4))
        Kappa4 = K_S4 @ np.linalg.inv(Ks_diag4)

        EPS_4 = - S4.T @ imposed_elongation_4  # modal scenario - size (s,) - (mm)
        a_4 = K_S4 @ EPS_4
        t_4 = S4 @ a_4
        e_4 = F4 @ t_4


        ####   Last stage - all modules ####
        imposed_elongation_5 = SelfStressScenario

        EPS_5 = - S.T @ imposed_elongation_5  # modal scenario - size (s,) - (mm)
        a_5 = K_S @ EPS_5
        t_5 = S @ a_5
        e_5 = F @ t_5

        # CURRENT self-stress levels / state identification



        #CORRECTIONS implementation

        Corrections_levels = np.array([-1.1, 2.2, 3.3, -4.4, -2.0])
        Corrections_EPS = F_S @ Corrections_levels
        selected_devices = np.array([4, 8, 13, 17, 18])-1
        S_row_selected = S[selected_devices,:].T
        Corrections_scenario = np.linalg.solve(-S_row_selected,Corrections_EPS)
        Corrections_a_temp = Ks_diag @ Corrections_EPS
        Corrected_a = Kappa @ Corrections_a_temp



        self.assertEqual(True, True)

    def test_SelfStressModesStiffness_CableStayedMast_paper(self):
        """

        :return:
        """

        Struct = StructureObj()

        NodesCoord = np.array([[0, 0, -1],
                               [0, 0, 2],
                               [-3, 0, 0],
                               [-1, 0, 0],
                               [1, 0, 0],
                               [3, 0, 0]])  # n = 6

        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False,
                              False, False, False,
                              False, False, False,
                              False, False, False])  # ndof = 2 degrees of freedom
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2],
                                     [1, 3],
                                     [1, 4],
                                     [1, 5]])

        ElementsType = np.ones((5,))  # b = 11 elements
        ElementsType[0] = -1  # struts

        # Bars can only be in compression and cables only in tension
        ElementsE = np.ones((5, 2)) * 70000  # MPa

        ElementsA = np.ones((5, 2)) * 50
        ElementsA[0, :] = 365

        Struct = StructureObj()
        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)

        # Structure's data
        F = np.diag(Struct.Initial.Flex * 1e6)  # flexibility matrix - size (b,b) - mm/kN
        K = np.linalg.inv(F)  # element stiffness matrix - size (b,b) - kN/mm
        A = Struct.Initial.AFree  # equilibrium matrix - size (ndof,b) - (no unit)
        s = Struct.Initial.SVD.s  # degree of static indeterminacy - scalar - (no unit)

        L = Struct.Initial.ElementsL * 1000  # assembled lengths - size (b,) - mm

        # Localized Self-stress modes After transformation (with Sanchez 2007).
        S = Struct.Initial.SVD.SS.T  # localized modes - size (b,s) - (no unit)
        #permut mode 2 and 3
        S2 = S[:,1].copy()
        S[:,1] = S[:,2].copy()
        S[:,2] = S2.copy()


        # Forces sensitivity matrices :
        SMt_S = -S @ np.linalg.inv(S.T @ F @ S) @ S.T  # size (b,b) - (kN/mm)
        # Conclusion : SMt_Vs = SMt_S

        # Stiffness K_S of localized self-stress modes S :
        K_S = np.linalg.inv(S.T @ F @ S)  # stiffness - size (s,s) - (kN/mm)
        F_S = S.T @ F @ S  # flexibility - size (s,s) - (mm/kN)
        SMa = -K_S @ S.T  # levels sensitivity matrix - size (s,b) - (kN/mm)

        ####   targeted forces   ####
        e_ = np.array([0, -4.9, -3.8, -3.8, -4.9])
        target_state = SMt_S @ e_

        #target_levels = SMa @ e_
        target_levels = np.array([4/(-1), 4/0.83853, 4/0.90139])
        target_state = S @ target_levels
        Modal_scenarios = F_S @ target_levels

        #symmetric prestress scenario
        constrain1 = np.array([[1, 0, 0, 0, 0]])  #e1=0
        constrain2 = np.array([[0, 0, 1, -1, 0]])  #e3 - e4 =0
        equations = np.vstack((-S.T,constrain1,constrain2))
        Modal_scenarios_extended = np.append(Modal_scenarios,np.array([0, 0]))
        prestress_scenario_sol = np.linalg.solve(equations,Modal_scenarios_extended)




        self.assertEqual(True, True)

    def test_ForceMethod_2bars(self): # change Test by test to run it
        """

        """
        Struct = StructureObj()
        L = 3 # m
        H = L

        NodesCoord = np.array([[-L,0,0],[L,0,0],[0,0,H]])
        IsDOFfree = np.array([False,False,False,False,False,False,True,False,True])
        ElementsEndNodes = np.array([[0,2],[1,2]])
        ElementsType = np.array([-1,-1])
        As = 50 # mm²
        Es = 70e3 # MPa
        ElementsA = np.array([As,As])
        ElementsE = np.array([Es,Es])

        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        A = Struct.Initial.AFree
        (ndof,b) = A.shape

        Ur = Struct.Initial.SVD.Ur_free_row.T
        # Um is null because no mechanism
        r = Struct.Initial.SVD.r #rank
        s = Struct.Initial.SVD.s
        S = np.zeros(A.shape)
        for i in range(r):
            S[i,i] = Struct.Initial.SVD.S[i]

        Vr_row = Struct.Initial.SVD.Vr_row
        Vs_row = Struct.Initial.SVD.Vs_row
        V_row = np.vstack((Vr_row,Vs_row))
        #Acheck = Ur@S@V_row #cross check the value of A


        #FORCE METHOD

        #lets assume {f}={2,3}.T #[kN]
        f = np.array([2,4])*1e3 #[N]
        fr  = Ur.T @ f#
        Sr_inv = np.diag(1/Struct.Initial.SVD.Sr) # matrice Lambda_r ^-1
        tr = Sr_inv @ fr


        A__ = np.linalg.pinv(A)
        A__check =  Vr_row.T @ Sr_inv @ Ur.T
        A__1 = np.linalg.inv(A)

        #CHECK OK

        t_r = A__ @ f # tensions in the 3 bars without knowing hyperstatic unknowns


        F = np.diag(Struct.Initial.Flex)
        K = np.diag(1/Struct.Initial.Flex)
        #F = np.eye(b)*500 #try
        #K = np.eye(b)/500#try
        Fs = Vs_row @ F @ Vs_row.T  # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        Fr = Vs_row @ F @ Vr_row.T

        #Vsq = V_row.T @ V_row #check that it is a V.T @ V and  V @ V.T both equal to the unit matrice I.
        #VsqT = V_row @ V_row.T


        #methode 1:
        Fr_Fs = np.hstack((Fr,Fs))
        MAT = np.vstack((S,Fr_Fs))
        fr_0 = np.hstack((fr,np.zeros((s,))))
        tr_ts = np.linalg.solve(MAT,fr_0)



        Ks = np.linalg.inv(Fs)
        SMa = -Ks @ Vs_row  # Sensitivity of the prestress level to a given elongation
        SMt = Vs_row.T @ SMa  # Sensitivity of the tensions to a given elongation
        I = np.eye(b)
        REDISTRIB = I + SMt @ F
        a = SMa @ F @ t_r
        t = REDISTRIB @ t_r
        # Se1 = F @ St1  # Sensitivity of the elastic elongations to a given imposed elongation

        B__ = A__.T  # the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        d = B__ @ F @ t
        # Sd1 = B__ @ (Se1 + np.eye(
        #     Struct.ElementsCount))  # Sensitivity of the displacements to a given imposed elongation, assuming the elongation do not activate the mechanism.
        #
        # K_SS =


        #DISPLACEMENT METHOD
        KLin = A @ K @ A.T
        d_check = np.linalg.solve(KLin,f)
        t_check = K @ A.T @ d_check
        #f_check = KLin @ d_check
        self.assertEqual(False, True)



    def test_ForceMethod_3bars(self): # change Test by test to run it
        """

        """
        Struct = StructureObj()
        L = 3 # m
        H = L

        NodesCoord = np.array([[-L,0,0],[0,0,0],[L,0,0],[0,0,H]])
        IsDOFfree = np.array([False,False,False,False,False,False,False,False,False,True,False,True])
        ElementsEndNodes = np.array([[0,3],[1,3],[2,3]])
        ElementsType = np.array([1,-1,1])
        As = 365 # mm²
        Es = 70e3 # MPa
        # Ac = 365*np.sqrt(2) # mm²
        Ac = 50  # mm²
        Ec = 70e3 # MPa
        ElementsA = np.array([Ac,As,Ac])
        ElementsE = np.array([Ec,Es,Ec])

        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        # # initial forces. note that results are independant from W since ?
        # W = 1000 #N
        # t1 = W/sin
        # t2 = t1*cos
        # Loads_Already_Applied = np.array([[0.0,0.0,0.0],[0.0,0.0,-W],[0.0,0.0,-W],[0.0,0.0,0.0]])
        # AxialForces_Already_Applied = np.array([t1,t2,t1])
        #
        # # t
        # Loads_To_Apply = np.zeros((12,1))
        # e = -0.01 # m elongation of the first cable
        # Elongations_To_Apply = np.array([e,0,0])
        #
        # S0.test_Main_LinearSolve_Force_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, ElementsA, ElementsE,
        #                                    AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
        #                                    Elongations_To_Apply)
        A = Struct.Initial.AFree
        (ndof,b) = A.shape

        Ur = Struct.Initial.SVD.Ur_free_row.T
        # Um is null because no mechanism
        r = Struct.Initial.SVD.r #rank
        s = Struct.Initial.SVD.s
        S = np.zeros(A.shape)
        for i in range(r):
            S[i,i] = Struct.Initial.SVD.S[i]

        Vr_row = Struct.Initial.SVD.Vr_row
        Vs_row = Struct.Initial.SVD.Vs_row
        V_row = np.vstack((Vr_row,Vs_row))
        #Acheck = Ur@S@V_row #cross check the value of A


        #FORCE METHOD

        #lets assume {f}={2,3}.T #[kN]
        f = np.array([2,4])*1e3 #[N]
        fr  = Ur.T @ f#
        Sr = np.diag(Struct.Initial.SVD.Sr)
        Sr_inv = np.diag(1/Struct.Initial.SVD.Sr) # matrice Lambda_r ^-1
        tr = Sr_inv @ fr


        A__ = np.linalg.pinv(A)
        A__check =  Vr_row.T @ Sr_inv @ Ur.T




        #CHECK OK

        t_r = A__ @ f # tensions in the 3 bars without knowing hyperstatic unknowns


        F = np.diag(Struct.Initial.Flex)
        K = np.diag(1/Struct.Initial.Flex)
        #F = np.eye(b)*500 #try
        #K = np.eye(b)/500#try
        Fs = Vs_row @ F @ Vs_row.T  # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        Fr = Vs_row @ F @ Vr_row.T

        #Vsq = V_row.T @ V_row #check that it is a V.T @ V and  V @ V.T both equal to the unit matrice I.
        #VsqT = V_row @ V_row.T



        #methode 1:
        Fr_Fs = np.hstack((Fr,Fs))
        MAT = np.vstack((S,Fr_Fs))
        fr_0 = np.hstack((fr,np.zeros((s,))))
        tr_ts = np.linalg.solve(MAT,fr_0)



        Ks = np.linalg.inv(Fs)
        SMa = -Ks @ Vs_row  # Sensitivity of the prestress level to a given elongation
        SMt = Vs_row.T @ SMa  # Sensitivity of the tensions to a given elongation
        I = np.eye(b)
        REDISTRIB = I + SMt @ F
        a = SMa @ F @ t_r
        t = REDISTRIB @ t_r
        # Se1 = F @ St1  # Sensitivity of the elastic elongations to a given imposed elongation

        B__ = A__.T  # the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        d = B__ @ F @ t
        # Sd1 = B__ @ (Se1 + np.eye(
        #     Struct.ElementsCount))  # Sensitivity of the displacements to a given imposed elongation, assuming the elongation do not activate the mechanism.
        #
        # K_SS =


        #DISPLACEMENT METHOD
        KLin = A @ K @ A.T

        Vr = Vr_row.T
        KLr = Sr @ Vr.T @ K @ Vr @ Sr
        U_K, S_K, V_K_row = np.linalg.svd(KLin)


        d_check = np.linalg.solve(KLin,f)
        KL_inv = np.linalg.inv(KLin)
        # d_check2 = KL_inv @ f
        K_inv_isostatic =  B__ @ F @ A__
        K_inv_hyperstatic =  B__ @ F @ SMt @ F @ A__


        t_check = K @ A.T @ d_check


        #f_check = KLin @ d_check
        self.assertEqual(False, True)


    def test_LinearForceMethod_2cables_symetric(self):
        """

        """
        Struct = StructureObj()

        L = 1000
        # L = 1

        NodesCoord = np.array([[0,0,0],[-L/2,0,0],[L/2,0,0]])
        ElementsEndNodes = np.array([[0,1],[0,2]])
        IsDOFfree = np.array([True,False,True,False,False,False,False,False,False])

        # note that results are independant from EA since statically determinate
        # Area = 50 # mm²
        # E = 70e3 # MPa
        Area = 1 # mm²
        E = 1 # MPa
        ElementsA = np.array([Area,Area])
        ElementsE = np.array([E,E])
        ElementsType = np.array([1,1])
        LoadsToApply = np.array([0, 0, 1,
                                 0, 0, 0,
                                 0, 0, 0]) * 1000


        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        F = np.diag(Struct.Initial.Flex)
        K = np.diag(1 / Struct.Initial.Flex)

        #INPUTS
        # lets assume {f}={2,3}.T #[kN]
        Struct.LoadsToApply = LoadsToApply

        t0 = np.array([1,1]) * 1000 #prestress [N]

        #SVD

        A = Struct.Initial.AFree
        (ndof, b) = A.shape

        Ur = Struct.Initial.SVD.Ur_free_row.T
        Um = Struct.Initial.SVD.Um_free_row.T
        r = Struct.Initial.SVD.r  # rank
        s = Struct.Initial.SVD.s
        S = np.zeros(A.shape)
        for i in range(r):
            S[i, i] = Struct.Initial.SVD.S[i]

        Vr_row = Struct.Initial.SVD.Vr_row
        Vs_row = Struct.Initial.SVD.Vs_row
        V_row = np.vstack((Vr_row, Vs_row))
        # Acheck = Ur@S@V_row #cross check the value of A

        # FORCE METHOD

        f = Struct.LoadsToApply[IsDOFfree] #loads applied on the free dof
        fr = Ur.T @ f  #extensional loads
        fm = Um.T @ f #inextensional loads

        ### extensional modes
        # EQUILIBRIUM
        Sr_inv = np.diag(1 / Struct.Initial.SVD.Sr)  # matrice Lambda_r ^-1
        tr = Sr_inv @ fr

        Fs = Vs_row @ F @ Vs_row.T  # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        Ks = np.linalg.inv(Fs)
        Fr = Vs_row @ F @ Vr_row.T
        R = -Ks @ Fr

        ts = R @ tr

        t = Vr_row.T @ tr + Vs_row.T @ ts

        # COMPATIBILITY
        er = Vr_row @ F @ t
        dr = Sr_inv @ er

        # INExtensional modes
        G = Struct.Geometric_Loads_Matrix(Struct.Initial.SVD, t0)
        Kgm = Um.T @ G

        dm = np.linalg.solve(Kgm, fm)

        d = Ur @ dr + Um @ dm


        #other way to write the same things
        SMa = -Ks @ Vs_row  # Sensitivity of the prestress level to a given elongation
        SMt = Vs_row.T @ SMa  # Sensitivity of the tensions to a given elongation

        A__ = np.linalg.pinv(A) #pseudo inverse of A
        A__check = Vr_row.T @ Sr_inv @ Ur.T
        # CHECK OK
        t1 = A__ @ f  # tensions due to extensional loads assuming no hyperstatic redistribution

        B__ = A__.T  # the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        d1 = B__ @ F @ t

        # # methode 1:
        # Fr_Fs = np.hstack((Fr, Fs))
        # Sr = np.diag(Struct.Initial.SVD.Sr)
        # MAT = np.vstack((S, Fr_Fs))
        # fr_0 = np.hstack((fr, np.zeros((s,))))
        # tr_ts = np.linalg.solve(MAT, fr_0)

        # DISPLACEMENT METHOD
        # KLin = A @ K @ A.T
        # d_check = np.linalg.solve(KLin, f)
        # t_check = K @ A.T @ d_check

        # #COMPARISON WITH DYNAMIC RELAXATION
        # StructDR = StructureObj()
        #
        # n_step = 50
        # LOADS_DR = np.zeros((2,))
        # TENSION_DR = np.zeros((2,))
        # DISPL_DR = np.zeros((2,))
        #
        # for i in np.arange(n_step):
        #
        #     loads = (i+1)*LoadsToApply/n_step
        #     loads_DR = loads[IsDOFfree]
        #     LOADS_DR = np.vstack((LOADS_DR,loads_DR))
        #     StructDR.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
        #                                             ElementsE,TensionInit=t0, LoadsToApply = loads, Dt=0.1)
        #
        #     tension_DR =  StructDR.Final.Tension
        #     TENSION_DR = np.vstack((TENSION_DR, tension_DR))
        #     Displ_DR = StructDR.Final.NodesCoord[IsDOFfree] - StructDR.Initial.NodesCoord[IsDOFfree]
        #     DISPL_DR = np.vstack((DISPL_DR, Displ_DR))
        #
        # LOADS_DR = LOADS_DR.T
        # TENSION_DR = TENSION_DR.T
        # DISPL_DR = DISPL_DR.T


        self.assertEqual(False, True)

    def test_LinearForceMethod_2cables_disymetric(self):
        """

        """
        Struct = StructureObj()

        L = 3000
        # L = 1

        NodesCoord = np.array([[0,0,0],[-L,0,0],[2*L,0,0]])
        ElementsEndNodes = np.array([[0,1],[0,2]])
        IsDOFfree = np.array([True,False,True,False,False,False,False,False,False])

        # note that results are independant from EA since statically determinate
        Area = 50 # mm²
        E = 70e3 # MPa
        # Area = 1 # mm²
        # E = 1 # MPa
        ElementsA = np.array([Area,Area])
        ElementsE = np.array([E,E])
        ElementsType = np.array([1,1])
        LoadsToApply = np.array([0, 0, 1,
                                 0, 0, 0,
                                 0, 0, 0]) * 1000


        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        F = np.diag(Struct.Initial.Flex)
        K = np.diag(1 / Struct.Initial.Flex)

        #INPUTS
        # lets assume {f}={2,3}.T #[kN]
        Struct.LoadsToApply = LoadsToApply

        t0 = np.array([1,1]) * 5000 #prestress [N]


        #SVD

        A = Struct.Initial.AFree
        (ndof, b) = A.shape

        Ur = Struct.Initial.SVD.Ur_free_row.T
        Um = Struct.Initial.SVD.Um_free_row.T
        r = Struct.Initial.SVD.r  # rank
        s = Struct.Initial.SVD.s
        S = np.zeros(A.shape)
        for i in range(r):
            S[i, i] = Struct.Initial.SVD.S[i]

        Vr_row = Struct.Initial.SVD.Vr_row
        Vs_row = Struct.Initial.SVD.Vs_row
        V_row = np.vstack((Vr_row, Vs_row))
        # Acheck = Ur@S@V_row #cross check the value of A



        # FORCE METHOD

        f = Struct.LoadsToApply[IsDOFfree] #loads applied on the free dof
        fr = Ur.T @ f  #extensional loads
        fm = Um.T @ f #inextensional loads

        ### extensional modes
        # EQUILIBRIUM
        Sr_inv = np.diag(1 / Struct.Initial.SVD.Sr)  # matrice Lambda_r ^-1
        tr = Sr_inv @ fr

        Fs = Vs_row @ F @ Vs_row.T  # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        Ks = np.linalg.inv(Fs)
        Fr = Vs_row @ F @ Vr_row.T
        R = -Ks @ Fr

        ts = R @ tr

        t = Vr_row.T @ tr + Vs_row.T @ ts

        # COMPATIBILITY
        er = Vr_row @ F @ t
        dr = Sr_inv @ er

        # INExtensional modes
        G = Struct.Geometric_Loads_Matrix(Struct.Initial.SVD, t0)
        Kgm = Um.T @ G

        dm = np.linalg.solve(Kgm, fm)

        d = Ur @ dr + Um @ dm


        #other way to write the same things
        SMa = -Ks @ Vs_row  # Sensitivity of the prestress level to a given elongation
        SMt = Vs_row.T @ SMa  # Sensitivity of the tensions to a given elongation

        A__ = np.linalg.pinv(A) #pseudo inverse of A
        A__check = Vr_row.T @ Sr_inv @ Ur.T
        # CHECK OK
        t1 = A__ @ f  # tensions due to extensional loads assuming no hyperstatic redistribution

        B__ = A__.T  # the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        d1 = B__ @ F @ t

        # # methode 1:
        # Fr_Fs = np.hstack((Fr, Fs))
        # Sr = np.diag(Struct.Initial.SVD.Sr)
        # MAT = np.vstack((S, Fr_Fs))
        # fr_0 = np.hstack((fr, np.zeros((s,))))
        # tr_ts = np.linalg.solve(MAT, fr_0)

        # DISPLACEMENT METHOD
        # KLin = A @ K @ A.T
        # d_check = np.linalg.solve(KLin, f)
        # t_check = K @ A.T @ d_check

        #COMPARISON WITH DYNAMIC RELAXATION
        StructDR = StructureObj()

        n_step = 50
        LOADS_DR = np.zeros((2,))
        TENSION_DR = np.zeros((2,))
        DISPL_DR = np.zeros((2,))

        for i in np.arange(n_step):

            loads = (i+1)*LoadsToApply/n_step
            loads_DR = loads[IsDOFfree]
            LOADS_DR = np.vstack((LOADS_DR,loads_DR))
            StructDR.test_MainDynamicRelaxation(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA,
                                                    ElementsE,TensionInit=t0, LoadsToApply = loads, Dt=0.1)

            tension_DR =  StructDR.Final.Tension
            TENSION_DR = np.vstack((TENSION_DR, tension_DR))
            Displ_DR = StructDR.Final.NodesCoord[IsDOFfree] - StructDR.Initial.NodesCoord[IsDOFfree]
            DISPL_DR = np.vstack((DISPL_DR, Displ_DR))

        LOADS_DR = LOADS_DR.T
        TENSION_DR = TENSION_DR.T
        DISPL_DR = DISPL_DR.T




        self.assertEqual(False, True)



    def test_LinearSolve_Force_Method_3cables(self): # change Test by test to run it
        """
        Tests on 3 cables \_/ (cfr Luo 2006 - Geometrically NL-FM for assemblies with infinitesimal mechanisms)
        test to check that RegisterData calculates correctly the number of nodes, elements, and supports. Test for 3 cables
        """
        S0 = StructureObj()
        #L = 3*0.160
        L = 3*1

        l = L/3 # length of the middle cable
        H = l/2

        l1 = np.sqrt(H**2 + l**2) # length of the extreme cables
        cos = l/l1
        sin = H/l1
        NodesCoord = np.array([[0.0,0.0,0.0],[L/3,0.0,-H],[2*L/3,0.0,-H],[L,0.0,0.0]])
        ElementsEndNodes = np.array([[0,1],[1,2],[2,3]])
        IsDOFfree = np.array([False,False,False,True,False,True,True,False,True,False,False,False])

        # note that results are independant from EA since statically determinate
        A = 50 # mm²
        E = 70e3 # MPa
        ElementsA = np.array([A,A,A])
        ElementsE = np.array([E,E,E])
        ElementsType = np.array([1,1,1])


        # initial forces. note that results are independant from W since ?
        Wi = 1 #N
        t1 = Wi/sin
        t2 = t1*cos
        Loads_Init = np.array([[0.0,0.0,0.0],[0.0,0.0,-Wi],[0.0,0.0,-Wi],[0.0,0.0,0.0]])
        Tension_Init = np.array([t1,t2,t1])

        # t
        Loads_To_Apply = np.zeros((12,1))
        e = -0.01 # m elongation of the first cable
        Elongations_To_Apply = np.array([e,0,0])

        S0.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE, TensionInit=Tension_Init,LoadsInit=Loads_Init )
        S0.Initial.ComputeState(S0,True,True)
        Kg = S0.Initial.Kgeo[S0.IsDOFfree].T[S0.IsDOFfree].T
        G = S0.Geometric_Loads_Matrix(S0.Initial.SVD, Tension_Init)
        Ur = S0.Initial.SVD.Ur_free_row.T
        Um = S0.Initial.SVD.Um_free_row.T
        U = np.hstack((Ur,Um))
        Vr = S0.Initial.SVD.Vr_row.T

        #link Kg and G

        A = S0.Initial.AFree
        K = np.diag(1/S0.Initial.Flex)

        KLin = A @ K @ A.T
        Sr = np.diag(S0.Initial.SVD.Sr)
        KLr = Sr @ Vr.T @ K @ Vr @ Sr
        U_K, S_K, V_K_row = np.linalg.svd(KLin)
        Lambda, W = np.linalg.eig(KLin)



        Kgmod = U.T @ Kg @ U


        Kgm = Um.T @ G
        Kgr = Ur.T @ G # = null ? NOOOOONNN ??? why ?

        DW = 1000 #N
        #Loads_To_Apply = np.array([[0,0,0],[-DW/2,0,-DW],[-DW/2,0,DW],[0,0,0]])
        Loads_To_Apply = np.array([[0,0,0],[0,0,-DW],[0,0,0],[0,0,0]])

        f = Loads_To_Apply.reshape((-1,))[IsDOFfree]
        fr = Ur.T @ f
        fm = Um.T @ f


        # S0.test_Main_LinearSolve_Force_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
        #                                    AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
        #                                    Elongations_To_Apply)
        #
        # Displacements_answer_free = np.array([-5.16,12.04,-5.16,10.32])*1e-3 #analytique solution
        # Displacements_answer = np.zeros((12, 1))
        # Displacements_answer[IsDOFfree] = Displacements_answer_free.reshape(-1,1)
        # self.assertEqual(np.allclose(S0.Displacements_Results,Displacements_answer,atol=1e-5),True)
        #
        # S1 = StructureObj()
        # e = -0.03  # m elongation of the first cable
        # Elongations_To_Apply = np.array([e, 0, 0])
        #
        # S1.test_Main_LinearSolve_Force_Method(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree, Elements_A, Elements_E,
        #                                       AxialForces_Already_Applied, Loads_To_Apply, Loads_Already_Applied,
        #                                       Elongations_To_Apply)
        #
        # Displacements_answer = Displacements_answer * 3
        # self.assertEqual(np.allclose(S1.Displacements_Results, Displacements_answer,atol=1e-5), True)

        self.assertEqual(False,True)

    def test_LinearForceMethod_SELFSTRESS_2cables_disymetric(self):
        """

        """
        Struct = StructureObj()

        L = 4 #m
        # L = 1

        NodesCoord = np.array([[0,0,0],[3*L/4,0,0],[L,0,0]])
        ElementsEndNodes = np.array([[0,1],[1,2]])
        IsDOFfree = np.array([False,False,False,True,False,True,False,False,False])

        # note that results are independant from EA since statically determinate
        Area = 400 # mm²
        E = 20e3 # MPa
        # Area = 1 # mm²
        # E = 1 # MPa
        ElementsA = np.array([Area,Area])
        ElementsE = np.array([E,E])
        ElementsType = np.array([1,1])



        Struct.test_MainAssemble(NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType, ElementsA, ElementsE)
        F = np.diag(Struct.Initial.Flex)
        K = np.diag(1 / Struct.Initial.Flex)

        #INPUTS
        # lets assume {f}={2,3}.T #[kN]
        ElongationsToApply = np.array([-30, 0]) /1000 #m

        Struct.ElongationsToApply = ElongationsToApply

        #SVD

        A = Struct.Initial.AFree
        (ndof, b) = A.shape

        Ur = Struct.Initial.SVD.Ur_free_row.T
        Um = Struct.Initial.SVD.Um_free_row.T
        r = Struct.Initial.SVD.r  # rank
        s = Struct.Initial.SVD.s
        S = np.zeros(A.shape)
        for i in range(r):
            S[i, i] = Struct.Initial.SVD.S[i]

        Vr_row = Struct.Initial.SVD.Vr_row
        Vs_row = Struct.Initial.SVD.Vs_row
        V_row = np.vstack((Vr_row, Vs_row))
        # Acheck = Ur@S@V_row #cross check the value of A


        Kmat = A@K@A.T

        KmatINV = np.linalg.pinv(Kmat)

        # FORCE METHOD

        # f = Struct.LoadsToApply[IsDOFfree] #loads applied on the free dof
        # fr = Ur.T @ f  #extensional loads
        # fm = Um.T @ f #inextensional loads
        #
        # ### extensional modes
        # # EQUILIBRIUM
        # Sr_inv = np.diag(1 / Struct.Initial.SVD.Sr)  # matrice Lambda_r ^-1
        # tr = Sr_inv @ fr
        #
        # Fs = Vs_row @ F @ Vs_row.T  # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        # Ks = np.linalg.inv(Fs)
        # Fr = Vs_row @ F @ Vr_row.T
        # R = -Ks @ Fr
        #
        # ts = R @ tr
        #
        # t = Vr_row.T @ tr + Vs_row.T @ ts
        #
        # # COMPATIBILITY
        # er = Vr_row @ F @ t
        # dr = Sr_inv @ er
        #
        # # INExtensional modes
        # G = Struct.Geometric_Loads_Matrix(Struct.Initial.SVD, t0)
        # Kgm = Um.T @ G
        #
        # dm = np.linalg.solve(Kgm, fm)
        #
        # d = Ur @ dr + Um @ dm
        #
        #
        # #other way to write the same things
        # SMa = -Ks @ Vs_row  # Sensitivity of the prestress level to a given elongation
        # SMt = Vs_row.T @ SMa  # Sensitivity of the tensions to a given elongation
        #
        # A__ = np.linalg.pinv(A) #pseudo inverse of A
        # A__check = Vr_row.T @ Sr_inv @ Ur.T
        # # CHECK OK
        # t1 = A__ @ f  # tensions due to extensional loads assuming no hyperstatic redistribution
        #
        # B__ = A__.T  # the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        # d1 = B__ @ F @ t

        # # methode 1:
        # Fr_Fs = np.hstack((Fr, Fs))
        # Sr = np.diag(Struct.Initial.SVD.Sr)
        # MAT = np.vstack((S, Fr_Fs))
        # fr_0 = np.hstack((fr, np.zeros((s,))))
        # tr_ts = np.linalg.solve(MAT, fr_0)

        # DISPLACEMENT METHOD
        # KLin = A @ K @ A.T
        # d_check = np.linalg.solve(KLin, f)
        # t_check = K @ A.T @ d_check

    def Test_NonLinearSolve_Force_Method_3cables(self): # change Test by test to run it
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

    def Test_Force_Density_Method_3cables(self): # change Test by test to run it
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
        S0.C = S0.ConnectivityMatrix(S0.NodesCount, S0.ElementsCount, S0.ElementsEndNodes)
        (S0.ElementsLFree, S0.Elements_Cos0) = S0.Compute_Elements_Geometry(S0.NodesCoord, S0.C)

        # (DR.A, DR.AFree, DR.AFixed) = DR.Compute_Equilibrium_Matrix(DR.Elements_Cos0, DR.C, DR.IsDOFfree)
        t0 = np.array([1, 10, 10])*1000
        q0 = t0/S0.ElementsLFree.reshape(-1, )
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
        (S1.ElementsLFree, S1.Elements_Cos0) = S1.Compute_Elements_Geometry(S1.NodesCoord, S1.C)
        t1 = q0 * S1.ElementsLFree

        # Loads_Already_Applied = np.array([[0.0,0.0,0.0],[0.0,0.0,-W],[0.0,0.0,-W],[0.0,0.0,0.0]])
        # TensionInit = np.array([t1,t2,t1])
        self.assertEqual(False, True)

    def Test_NonLinear_Prestress_3cables(self): # change Test by test to run it
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
        S0.CoreAssemble()
        S0.ElementsLFree = S0.Elements_L.copy()
        S0.Elements_Cos0 = S0.Elements_Cos.copy()
        S0.Km = S0.Compute_StiffnessMat_Matrix(S0.A, S0.Elements_L, S0.ElementsA, S0.ElementsE)
        S0.Km_free = S0.Compute_StiffnessMat_Matrix(S0.AFree, S0.Elements_L, S0.ElementsA, S0.ElementsE)
        S0.F = S0.Flexibility_Matrix(S0.ElementsE, S0.ElementsA, S0.ElementsLFree)
        # DR.SVD = DR.SVD_Equilibrium_Matrix(DR.AFree)

        # Solve B0.U0 = e_inelastic
        # DR.Displacements_Results = np.linalg.solve(DR.AFree.transpose(),DR.Elongations_To_Apply) # try to solve 3 eq with 2 unknowns raise a LinAlgError because AFree is not square
        S0.Displacements_Results = \
        np.linalg.lstsq(S0.AFree.transpose(), S0.Elongations_To_Apply.reshape(-1), rcond=0.001)[0]

        # Or Solve K.U = f = At = Ake
        t_inelastic = np.linalg.inv(S0.F) @ S0.Elongations_To_Apply
        f_inelastic = S0.AFree @ t_inelastic
        Displacements_Results_free = np.linalg.solve(S0.Km_free, f_inelastic)

        ## ITERATION 1
        # Update
        Displacements_Results = np.zeros(NodesCoord.shape)
        Displacements_Results[IsDOFfree] = Displacements_Results_free
        NodesCoord1 = S0.NodesCoord + Displacements_Results
        S1 = S0.NewStructureObj(NodesCoord1, np.zeros((S0.ElementsCount, 1)), np.zeros((3 * S0.NodesCount, 1)))
        S1.Elongations_To_Apply = S0.Elongations_To_Apply.copy()

        # Compute Equilibrium matrix
        (S1.ElementsL, S1.ElementsCos) = S1.ElementsLengthsAndCos(S1.NodesCoord, S1.C)  # cos = (X2_def - X1_def)/L_def
        (S1.A, S1.AFree, S1.AFixed) = S1.EquilibriumMatrix(None, S1.ElementsCos)

        # find e_elastic = B1@U0
        e_elastic = S1.AFree.transpose() @ Displacements_Results_free  # AFree contient les cos dans la position déformée avec les longueurs déformées
        e_tot = e_elastic - S1.Elongations_To_Apply

        # find total forces
        L_def_approx = S0.ElementsLFree.reshape(-1, 1) + S0.Elongations_To_Apply
        S1.Flex = S1.Flexibility_Matrix(S1.ElementsE, S1.ElementsA, L_def_approx.reshape(-1, ))
        k1_bsc = np.linalg.inv(S1.Flex)
        t_tot = k1_bsc @ e_tot

        f_unbalanced = -(S1.AFree @ t_tot)  # unbalanced = external load - resisting forces (external load = 0)
        S1.Km_free = S1.AFree @ k1_bsc @ (S1.AFree.transpose())
        Displacements1_Results_free = np.linalg.solve(S1.Km_free, f_unbalanced)

        ## ITERATION 2
        # Update
        Displacements1_Results = np.zeros(NodesCoord.shape)
        Displacements1_Results[IsDOFfree] = Displacements1_Results_free
        NodesCoord2 = S1.NodesCoord + Displacements1_Results
        S2 = S1.NewStructureObj(NodesCoord2, np.zeros((S0.ElementsCount, 1)), np.zeros((3 * S0.NodesCount, 1)))

        # Compute Equilibrium matrix
        (S2.ElementsL, S2.ElementsCos) = S2.ElementsLengthsAndCos(S2.NodesCoord, S2.C)  # cos = (X2_def - X1_def)/L_def
        (S2.A, S2.AFree, S2.AFixed) = S2.EquilibriumMatrix(None, S2.ElementsCos)

        # find e_elastic = B1@U0
        e2_elastic = S2.AFree.transpose() @ Displacements1_Results_free  # AFree contient les cos dans la position déformée avec les longueurs déformées
        e2_tot = e2_elastic

        # find total forces
        # L_def_approx = DR.ElementsLFree.reshape(-1,1)+DR.Elongations_To_Apply
        # S2.Flex = S2.Flexibility_Matrix(S2.ElementsE, S2.ElementsA, L_def_approx.reshape(-1,))
        # k2_bsc = np.linalg.inv(S2.Flex)
        t2_tot = k1_bsc @ e2_tot

        f2_unbalanced = -(S2.AFree @ t2_tot)  # unbalanced = external load - resisting forces (external load = 0)
        S2.Km_free = S2.AFree @ k1_bsc @ (S2.AFree.transpose())
        Displacements2_Results_free = np.linalg.solve(S2.Km_free, f2_unbalanced)
    # endregion

if __name__ == '__main__':
    unittest.main()