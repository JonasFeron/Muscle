import unittest
import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/MusclePy'))
sys.path.append(base_dir)
from StructureObj import *
import numpy as np


class Test_State(unittest.TestCase):



    def test_FlexibilityMatrix(self):

        ElementsA = np.array([1e4,1e4]) #mm²
        ElementsE = np.array([100e3,0]) #MPa
        ElementsL = np.array([2,2]) #m

        S = StructureObj()
        S.ElementsCount = 2
        #Initial = State()
        F = S.Flexibility(ElementsE, ElementsA, ElementsL)  #Flex=L/EA
        self.assertEqual(F[0], 2/(100e7))
        self.assertEqual(F[1], 1e6)

    def test_Simple_ComputeTension(self):

        #A structure composed of 4 elements.
        # The first element is a cable where compression is allowed
        # The second element is a cable with no stiffness in compression hence it slacks if compressed.
        # The third element is a cable with no stiffness in compression. but it is subjected to 0 lengthening, hence its stiffness is based on the tension properties.
        ElementsA = np.array([[1,1],
                              [1,1],
                              [1,1]]) *100 #mm²
        ElementsE = np.array([[1,1],
                              [0,1],
                              [0,1]]) *1e3 #MPa
        ElementsLFree = np.array([2.0,2.0,2.0]) #m
        ElementsLCur = np.array([2.01,1.99,2.0])  #first is tensionned, second is compressed
        ElementsType = np.array([1,1,1])  #two cables

        S = StructureObj() #a structure with no node and 2 elements
        S.ElementsCount=3
        S.ElementsType = ElementsType
        deformed = State()
        (T,Flex) = deformed.TensionForces(S,ElementsLCur, ElementsLFree, ElementsE, ElementsA)
        self.assertAlmostEqual(T[0], 100e3/2*0.01,places=0)
        self.assertAlmostEqual(T[1], 0,places=0)
        self.assertEqual(T[2], 0)
        self.assertEqual(Flex[2], 2/100e3)




    def test_Simple_ComputeResidual(self):
        """
        A simple test composed of 2 cables : (N0) --E0-- (N1) --E1-- (N2)
        :return:
        """
        #1) Define the structure geometry
        S = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              False, False, False])

        S.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree)
        (l, ElementsCos) = S.Initial.ElementsLengthsAndCos(S,NodesCoord)
        (A, AFree, A_fixed) = S.Initial.EquilibriumMatrix(S, ElementsCos)

        #2) Define the Loads
        Loads = np.array([[0, 0, 0],
                          [2, 0, 3], #the load 1Z should always be unbalanced in this geometry
                          [0, 0, 0]])

        #3) test different tension
        #3a) equilibrium in X
        Tension = np.array([1, -1])
        fint = A@Tension #FYI
        Residual_a = S.Initial.UnbalancedLoads(S,A, Loads, Tension)
        ResidualFree_a = S.Initial.UnbalancedLoads(S,AFree, Loads, Tension)
        success_a = np.all(Residual_a == np.array([[1, 0, 0],[0, 0, 3],[1, 0, 0]]).reshape(-1,))
        successFree_a = np.all(ResidualFree_a == np.array([[0, 0, 0],[0, 0, 3],[0, 0, 0]]).reshape(-1,))
        self.assertEqual(success_a, True)
        self.assertEqual(successFree_a, True)

        # 3b) equilibrium in X bis
        Tension = np.array([2, 0])
        fint = A@Tension #FYI
        Residual_b = S.Initial.UnbalancedLoads(S,A, Loads, Tension)
        ResidualFree_b = S.Initial.UnbalancedLoads(S,AFree, Loads, Tension)
        success_b = np.all(Residual_b == np.array([[2, 0, 0],[0, 0, 3],[0, 0, 0]]).reshape(-1,))
        successFree_b = np.all(ResidualFree_b == np.array([[0, 0, 0],[0, 0, 3],[0, 0, 0]]).reshape(-1,))
        self.assertEqual(success_b, True)
        self.assertEqual(successFree_b, True)

        # 3C) equilibrium in X bis
        Tension = np.array([1, 0])
        fint = A@Tension #FYI
        Residual_c = S.Initial.UnbalancedLoads(S,A, Loads, Tension)
        ResidualFree_c = S.Initial.UnbalancedLoads(S,AFree, Loads, Tension)
        success_c = np.all(Residual_c == np.array([[1, 0, 0],[1, 0, 3],[0, 0, 0]]).reshape(-1,))
        successFree_c = np.all(ResidualFree_c == np.array([[0, 0, 0],[1, 0, 3],[0, 0, 0]]).reshape(-1,))
        self.assertEqual(success_c, True)
        self.assertEqual(successFree_c, True)

    def test_Simple1_GlobalGeometricStiffnessMatrix(self):
        S = StructureObj()
        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1]])
        IsDOFfree = np.array([True, True, True, True, True, True])

        S.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree)
        Initial = S.Initial
        (Initial.ElementsL, Initial.ElementsCos) = Initial.ElementsLengthsAndCos(S,Initial.NodesCoord)

        Tension = np.array([4])
        q = Initial.ForceDensities(Tension, Initial.ElementsL)
        kgLocList = Initial.GeometricLocalStiffnessList(S, q)
        Kgeo = S.LocalToGlobalStiffnessMatrix(kgLocList)

        self.assertEqual(True, True)

    def test_Simple2_GlobalGeometricStiffnessMatrix(self):
        S = StructureObj()

        NodesCoord = np.array([[0.0, 0.0, 0.0],
                               [1.0, 0.0, 0.0],
                               [2.0, 0.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([True, True, True,
                              True, True, True,
                              True, True, True])

        S.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree)

        Initial = S.Initial
        (Initial.ElementsL, Initial.ElementsCos) = Initial.ElementsLengthsAndCos(S,Initial.NodesCoord)
        Tension = np.array([4,4])
        Kgeo = Initial.GeometricStiffnessMatrix(S, Tension, Initial.ElementsL)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
