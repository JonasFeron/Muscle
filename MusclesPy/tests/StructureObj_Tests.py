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
        Struct.Initial.ElementsE = Struct.ElementsInTensionOrCompression(ElementsType,ElementsE)
        Struct.Initial.ElementsA = Struct.ElementsInTensionOrCompression(ElementsType, ElementsA)

        (l, ElementsCos) = Struct.Initial.ElementsLengthsAndCos(Struct, NodesCoord)
        (A, AFree, AFixed) = Struct.Initial.EquilibriumMatrix(Struct, ElementsCos)
        Struct.Initial.SVD.SVDEquilibriumMatrix(Struct, AFree)
        #S = Struct.Initial.SVD.Vs_row.T #Self-stress matrix
        S = Struct.Initial.SVD.SS.T  # Self-stress matrix
        Struct.Initial.Flex = Struct.Flexibility(Struct.Initial.ElementsE, Struct.Initial.ElementsA, l)
        F = np.diag(Struct.Initial.Flex)
        Ke = np.diag(1/Struct.Initial.Flex)

        a = 1500 # prestress level [N]
        t0 = S * a # prestress forces [N] # assumption no self-weight
        q = Struct.Initial.ForceDensities(t0, l) #
        kgLocList = Struct.Initial.GeometricLocalStiffnessList(Struct, q)
        Kgeo = Struct.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Struct.IsDOFfree].T[Struct.IsDOFfree].T

        BFree = AFree.T # the compatibility matrix

        #According to [1] and [2]
        SFS = S.T @ F @ S # This is the structural flexibility ! because the shortening of a flexible cable increase as much the prestress level than the lengthening of a strut
        Ks = np.linalg.inv(SFS)
        Sa = -Ks @ S.T # Sensitivity of the prestress level to a given elongation
        St1 = S @ Sa # Sensitivity of the tensions to a given elongation
        Se1 = F @ St1 # Sensitivity of the elastic elongations to a given imposed elongation

        B__ = np.linalg.pinv(BFree) #the pseudo inverse of the compatibility matrix to get rid of the mechanism  https://numpy.org/doc/stable/reference/generated/numpy.linalg.pinv.html
        Sd1 = B__ @ (Se1 + np.eye(Struct.ElementsCount)) #Sensitivity of the displacements to a given imposed elongation, assuming the elongation do not activate the mechanism.

        # According to [1]
        Kmat = AFree @ Ke @ BFree
        Kmat__ = np.linalg.pinv(Kmat)
        Sd2 = Kmat__ @ AFree @ Ke #equivalent to Sd1
        St2 = Ke @ BFree @ Sd2 - Ke #equivalent to St1
        SD2 = np.around(Sd2.reshape((1,-1)),4)

        # According to [1]

        Ktan__ = np.linalg.inv(Kmat+KgeoFree)
        Sd3 = Ktan__ @ AFree @ Ke
        St3 = Ke @ BFree @ Sd3 - Ke
        CT3 = Sd3[:,8]

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

    def Test_LinearSolve_Force_Method_3cables(self): # change Test by test to run it
        """
        Tests on 3 cables \_/ (cfr Luo 2006 - Geometrically NL-FM for assemblies with infinitesimal mechanisms)
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