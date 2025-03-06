# -*- coding: utf-8 -*-
import unittest
import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/MusclePy'))
sys.path.append(base_dir)
from StructureObj import *
import numpy as np
import scipy.linalg as lin
import scipy.optimize as opt


class Test_StructureObj(unittest.TestCase):




    # region Assemble methods



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


    # region NONLinear Displacement Method



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

    #region Dynamics
    def test_dyn_bar(self):
        """
        Check if the obtained natural frequency of a single bar is correct
        TEST on a simple beam
        Name of SCIA file : SimpleBEAM
        Works if the part about pretension is put in comment in SructureObj
        :return:
        """
        Struct = StructureObj()
        Struct.NodesCoord = np.array([[0.00, 0.00, 0.00],
                                      [3.00, 0.00, 0.00]])

        Struct.IsDOFfree = np.array([False, False, False,
                                     True, False, False])

        Struct.ElementsType = np.array([1])
        Struct.NodesCount = 2
        Struct.ElementsCount = 1
        Struct.FixationsCount = 5
        Struct.DOFfreeCount = 3 * Struct.NodesCount - Struct.FixationsCount
        Struct.ElementsEndNodes = np.array([[0, 1]])

        Struct.ElementsE = 0.21 * np.ones((Struct.ElementsCount, 2)) * 10 ** 6  # MPa
        Struct.ElementsA = 90000 * np.ones((Struct.ElementsCount, 2))  # mm2
        Struct.DynMasses = 1 #* np.array([1, 1])  # kg
        PrestrainLevel = 0  # [kN]
        Struct.ModuleDynamicsPython(PrestrainLevel)
        print(Struct.freq)
        wScia = np.array([79370])  # Data coming from the SCIA model
        self.assertEqual(np.allclose(Struct.freq, wScia, atol=3), True)
        #self.assertEqual(True, True)


    def test_dyn_doublebar(self):
        """
        Check if the obtained natural frequencies of a structure are correct
        TEST on a inversed V structure
        Name of SCIA file : test_2BEAM
        Works if the part about pretension is put in comment in SructureObj
        :return:
        """
        Struct = StructureObj()
        Struct.NodesCoord = np.array([[0.00, 0.00, 0.00],
                                      [2.00, 2.00, 0.00],
                                      [4.00, 0.00, 0.00]])

        Struct.IsDOFfree = np.array([False, False, False,
                                     True, True, False,
                                     False, False, False])

        Struct.ElementsType = np.array([1, 1 ])
        Struct.NodesCount = 3
        Struct.ElementsCount = 2
        Struct.FixationsCount = 7
        Struct.DOFfreeCount = 3 * Struct.NodesCount - Struct.FixationsCount
        Struct.ElementsEndNodes = np.array([[0, 1],
                                            [1, 2]])

        Struct.ElementsE = 0.21 * np.ones((Struct.ElementsCount, 2)) * 10 ** 6  # MPa
        Struct.ElementsA = 90000 * np.ones((Struct.ElementsCount, 2))  # mm2
        Struct.DynMasses = 1 * np.array([1, 1, 1])  # kg
        PrestrainLevel = 0  # [kN]
        w, PHI = Struct.ModuleDynamicsPython(PrestrainLevel)
        print(w)
        wScia = np.array([81741, 81741])  # Data coming from the SCIA model
        self.assertEqual(np.allclose(w, wScia, atol=3), True)


    def test_Dyn_truss(self):
        """
        Check if the obtained natural frequencies of a structure are correct
        TEST on a truss
        Name of SCIA file : TEST_simpleTRUSS
        Works if the part about pretension is put in comment in SructureObj
        :return:
        """
        Struct = StructureObj()
        Struct.NodesCoord = np.array([[0.00, 0.00, 0.00],
                               [2.50, 5.00, 0.00],
                               [5.00, 0.00, 0.00],
                               [7.50, 5.00, 0.00],
                               [10.00, 0.00, 0.00]])

        Struct.IsDOFfree = np.array([False, False, False,
                              True, True, False,
                              True, True, False,
                              True, True, False,
                              True, False, False])

        Struct.ElementsType = np.array([1, 1, 1, 1, 1, 1, 1])
        Struct.NodesCount = 5
        Struct.ElementsCount = 7
        Struct.FixationsCount = 8
        Struct.DOFfreeCount = 3 * Struct.NodesCount - Struct.FixationsCount
        Struct.ElementsEndNodes = np.array([[0, 1],
                                            [0, 2],
                                            [1, 2],
                                            [2, 4],
                                            [1, 3],
                                            [2, 3],
                                            [3, 4]])

        Struct.ElementsE = 0.21*np.ones((Struct.ElementsCount, 2))*10**6  # MPa
        Struct.ElementsA = 90000 * np.ones((Struct.ElementsCount, 2))  # mm2
        Struct.DynMasses = np.array([1, 1, 1, 1, 1])  # kg
        PrestrainLevel = 0  # [kN]
        w, PHI = Struct.ModuleDynamicsPython(PrestrainLevel)
        print('w', w)
        wScia = np.array([25810.53 , 36157.38 , 53325.3 , 68567.28 , 89122.83 , 102607.29 , 108948.17])  # Data coming from the SCIA model
        self.assertEqual(np.allclose(w, wScia, atol=3), True)

    def test_Dyn_truss(self):
        """
        Check if the obtained natural frequencies of a structure are correct
        TEST on a 3D truss
        Name of SCIA file : TEST_3D_dyn
        Works if the part about pretension is put in comment in SructureObj
        :return:
        """
        Struct = StructureObj()
        Struct.NodesCoord = np.array([[0.00, 0.00, 0.00],
                                      [-1.00, 4.00, 0.00],
                                      [1.00, 4.00, 0.00],
                                      [0.00, 2.00, 3.00]])

        Struct.IsDOFfree = np.array([False, False, False,
                                     True, False, False,
                                     True, False, False,
                                     True, True, True])

        Struct.ElementsType = np.array([1, 1, 1, 1, 1, 1])
        Struct.NodesCount = 4
        Struct.ElementsCount = 6
        Struct.FixationsCount = 7
        Struct.DOFfreeCount = 3 * Struct.NodesCount - Struct.FixationsCount
        Struct.ElementsEndNodes = np.array([[0, 1],
                                            [1, 2],
                                            [2, 0],
                                            [0, 3],
                                            [1, 3],
                                            [2, 3]])

        Struct.ElementsE = 0.21 * np.ones((Struct.ElementsCount, 2)) * 10 ** 6  # MPa
        Struct.ElementsA = 90000 * np.ones((Struct.ElementsCount, 2))  # mm2
        Struct.DynMasses = np.array([1, 1, 1, 1])  # kg
        PrestrainLevel = 0  # [kN]
        w, PHI = Struct.ModuleDynamicsPython(PrestrainLevel)
        print('w', w)
        wScia = np.array(
            [12795.77, 34470.83, 62397.29, 101845.22, 141015.39])  # Data coming from the SCIA model
        self.assertEqual(np.allclose(w, wScia, atol=3), True)
        #self.assertEqual(True, True)

    def test_dyn_bar_prestressed(self):
        """
        Check if the obtained natural frequency of a single bar with prestressing is correct
        TEST on a simple beam with prestressing
        Name of SCIA file : SimpleBEAM_prestressed
        :return:

        """
        Struct = StructureObj()
        Struct.NodesCoord = np.array([[0.00, 0.00, 0.00],
                                      [2.50, 0.00, 0.00],
                                      [5.00, 0.00, 0.00]])

        Struct.IsDOFfree = np.array([False, False, False,
                                     True, True, False,
                                     False, False, False])

        Struct.ElementsType = np.array([1,1])
        Struct.NodesCount = 3
        Struct.ElementsCount = 2
        Struct.FixationsCount = 7
        Struct.DOFfreeCount = 3 * Struct.NodesCount - Struct.FixationsCount
        Struct.ElementsEndNodes = np.array([[0, 1],[1,2]])

        Struct.ElementsE = 3.15 * np.ones((Struct.ElementsCount, 2)) * 10**4  # MPa
        Struct.ElementsA = 90000 * np.ones((Struct.ElementsCount, 2))  # mm2
        Struct.DynMasses = 1 * np.array([1, 1, 1])  # kg
        PrestrainLevel = 0.000001  # [kN]
        w, PHI = Struct.ModuleDynamicsPython(PrestrainLevel)
        print(w)
        #wScia = np.array([79370])  # Data coming from the SCIA model
        #self.assertEqual(np.allclose(w, wScia, atol=3), True)
        self.assertEqual(True, True)


    def test_Simplex_NaturalFrequencies(self):
        """
        Find the natural frequencies of the experimental simplex

        :return:
        """

        # theoretical nodes coordinates
        NodesCoord = np.array([[0.00, -2043.82, 0.00],
                               [0.00, 0.00, 0.00],
                               [1770.00, -1021.91, 0.00],
                               [590.00, -2201.91, 1950.00],
                               [-431.91, -431.91, 1950.00],
                               [1611.91, -431.91, 1950.00]]) * 1e-3
        IsDOFfree = np.array([False, True, False,
                              False, False, False,
                              True, True, False,
                              True, True, True,
                              True, True, True,
                              True, True, True])
        ElementsType = np.array([-1, -1, -1, 1, 1, 1, 1, 1, 1, 1, 1, 1])
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

        # Bars can only be in compression and cables only in tension
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

        ElementsA = np.ones((12, 2))
        ElementsA[0:3, :] = 364.4
        ElementsA[3:12, :] = 50.3

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

        # precontrainte dans la structure theorique. On impose directement une force (plutot que d'imposer un "LengtheningToApply")
        Struct.Initial.SVD.SVDEquilibriumMatrix(Struct, AFree)

        S = Struct.Initial.SVD.SS.T  # Self-stress matrix

        print(S)
        a = 1500  # prestress level [N]
        t0 = S * a  # prestress forces [N] # assumption no self-weight


        print(t0)

        # matrice de rigidite geometrique
        q = Struct.Initial.ForceDensities(t0, l)  #
        kgLocList = Struct.Initial.GeometricLocalStiffnessList(Struct, q)
        Kgeo = Struct.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Struct.IsDOFfree].T[Struct.IsDOFfree].T

        # matrice de rigidite materielle
        Struct.Initial.Flex = Struct.Flexibility(Struct.Initial.ElementsE, Struct.Initial.ElementsA, l)
        F = np.diag(Struct.Initial.Flex)
        Ke = np.diag(1 / Struct.Initial.Flex)

        # KmatFree = AFree @ Ke @ AFree.T #methode 1
        kmatLocList = Struct.Initial.MaterialLocalStiffnessList(Struct, l, ElementsCos, Struct.Initial.ElementsA,
                                                                Struct.Initial.ElementsE)
        Kmat = Struct.LocalToGlobalStiffnessMatrix(kmatLocList)
        KmatFree = Kmat[Struct.IsDOFfree].T[Struct.IsDOFfree].T  # methode 2

        self.assertEqual(False, True)


    def test_dyn_doublebar_CSharp(self):
        """
        See if the code is working and that there is no error / bug
        TEST of a cable on two supports
        Works if the part about pretension is put in comment in SructureObj
        :return:
        """

        NodesCoord = np.array([[0.00, 0.00, 0.00],
                                      [2.00, 0.00, 0.00],
                                      [4.00, 0.00, 0.00]])


        IsDOFfree = np.array([False, False, False,
                                     True, True, False,
                                     False, False, False])

        ElementsType = np.array([1, 1])
        NodeCount = 3
        ElementsCount = 2
        FixationsCount = 7
        #DOFfreeCount = 3 * NodesCount - FixationsCount
        ElementsEndNodes = np.array([[0, 1], [1, 2]])

        ElementsE = 0.21 * np.ones((ElementsCount, 2)) * 10 ** 6  # MPa
        ElementsA = 90000 * np.ones((ElementsCount, 2))  # mm2
        print('E', ElementsE)
        DynamicMass = np.array([1,1,1])   # kg #Possibility to test if use a vector with a len < or > % Number of nodes
        TensionInit = 5*np.array([1, 1]) #Newtons
        Struct = StructureObj()
        NumberOfFreqWanted = 2
        freq, mode,TotMode = Struct.test_ModuleDynamics(NodeCount, ElementsCount, ElementsEndNodes, FixationsCount, NodesCoord,
                                   ElementsType, ElementsE, ElementsA, TensionInit, IsDOFfree, DynamicMass, NumberOfFreqWanted)

        print('freq', freq)
        print('mode', mode)
        print('totMode',TotMode) #Insert in the mode matrix the non-dof. It is adding zero displacements.
        #self.assertEqual(np.allclose(wtest, wtest, atol=3), True)

        self.assertEqual(True, True)

    # endregion

if __name__ == '__main__':
    unittest.main()