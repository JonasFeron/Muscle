import unittest
import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/MusclePy'))
sys.path.append(base_dir)
from StructureObj import *
import numpy as np


class MyTestCase(unittest.TestCase):

    def test_Simple_ComputeElementsLengthsAndCos(self):
        """
        Check that ComputeElementsLengthsAndCos calculates correctly the lengths of the elements and their cos directors compared to Grasshopper results. Test for 2 cables (*--c1--*--c2--*)
        """
        S = StructureObj()
        NodesCoord = np.array([[0.0, 1.0, 0.0], [1.0, 1.0, 0.0], [2.0, 1.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1], [1, 2]])
        IsDOFfree = np.array([False, False, False, True, True, True, False, False, False])

        S.InitialData(NodesCoord,ElementsEndNodes,IsDOFfree)

        Initial = S.Initial
        (Initial.ElementsL, Initial.ElementsCos) = Initial.ElementsLengthsAndCos(S, Initial.NodesCoord)

        #check the results
        # test of comparison with Grasshopper
        ElementsL0_GH = np.array([1.0,1.0])
        CosX_GH = np.array([1.0, 1.0])
        CosY_GH = np.array([0.0, 0.0])
        CosZ_GH = np.array([0.0, 0.0])

        successShape = Initial.ElementsL.shape == (2,) and Initial.ElementsCos.shape == (2,3)
        successL = (Initial.ElementsL == ElementsL0_GH).all()
        successCosX = (Initial.ElementsCos[:, 0] == CosX_GH).all()
        successCosY = (Initial.ElementsCos[:, 1] == CosY_GH).all()
        successCosZ = (Initial.ElementsCos[:, 2] == CosZ_GH).all()

        self.assertEqual(successShape, True)
        self.assertEqual(successL, True)
        self.assertEqual(successCosX, True)
        self.assertEqual(successCosY, True)
        self.assertEqual(successCosZ, True)

    def test_ComputeEquilibriumMatrix_2cables(self):
        S = StructureObj()
        NodesCoord = np.array([[0.0, 0, 0],
                               [1.0, 0, 0],
                               [2.0, 0, 0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, True, True,
                              False, False, False])

        S.InitialData(NodesCoord,ElementsEndNodes,IsDOFfree)

        (l,ElementsCos) = S.Initial.ElementsLengthsAndCos(S,NodesCoord)
        (A, A_free, A_fixed) = S.Initial.EquilibriumMatrix(S, ElementsCos)

        A_free_answer = np.array([[1.0, -1.0],
                                  [0.0, 0.0],
                                  [0.0, 0.0]])
        success  = (A_free == A_free_answer).all()

        self.assertEqual(success,True)



    def test_SVDEquilibriumMatrix_2cables(self):
        S = StructureObj()
        NodesCoord = np.array([[0.0, 0, 0],
                               [1.0, 0, 0],
                               [2.0, 0, 0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, True, True,
                              False, False, False])

        S.InitialData(NodesCoord,ElementsEndNodes,IsDOFfree)

        (l,ElementsCos) = S.Initial.ElementsLengthsAndCos(S,NodesCoord)
        (A, AFree, AFixed) = S.Initial.EquilibriumMatrix(S, ElementsCos)
        S.Initial.SVD.SVDEquilibriumMatrix(S, AFree)

        r_answer = 1
        self.assertEqual(S.Initial.SVD.r, r_answer)

        s_answer = 1
        self.assertEqual(S.Initial.SVD.s, s_answer)

        SS_answer = np.array([[-1.0, -1.0]])
        successSS = np.allclose(S.Initial.SVD.SS,SS_answer)
        self.assertEqual(successSS, True)

        m_answer = 2
        self.assertEqual(S.Initial.SVD.m, m_answer)

        Um_answer= np.array([[0.0, 1.0, 0.0], [0.0, 0.0, 1.0]])
        successUm = np.allclose(S.Initial.SVD.Um_free_row,Um_answer)
        self.assertEqual(successUm, True)

    def test_SVDEquilibriumMatrix_2cables_FiniteMechanism(self):
        S = StructureObj()
        NodesCoord = np.array([[0.0, 0, 0],
                               [1.0, 0, 0],
                               [2.0, 0, 0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              True, False, False])

        S.InitialData(NodesCoord,ElementsEndNodes,IsDOFfree)
        S.C = S.ConnectivityMatrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)

        (l,ElementsCos) = S.Initial.ElementsLengthsAndCos(S,NodesCoord)
        (A, AFree, AFixed) = S.Initial.EquilibriumMatrix(S, ElementsCos)
        S.Initial.SVD.SVDEquilibriumMatrix(S, AFree)

        s_answer = 0
        self.assertEqual(S.Initial.SVD.s, s_answer)


        m_answer = 1
        self.assertEqual(S.Initial.SVD.m, m_answer)

        Um_answer= np.array([[0.0, -1.0, 0.0]])
        successUm = np.allclose(S.Initial.SVD.Um_free_row,Um_answer)
        self.assertEqual(successUm, True)

    def test_SVDEquilibriumMatrix_3cables(self):
        S = StructureObj()
        NodesCoord = np.array([[0.0, 0, 0],
                               [0.16, 0, -0.08],
                               [0.32, 0, -0.08],
                               [0.48, 0, 0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2],
                                     [2, 3]])
        IsDOFfree = np.array([False, False, False,
                              True, False, True,
                              True, False, True,
                              False, False, False])

        S.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree)

        (l, ElementsCos) = S.Initial.ElementsLengthsAndCos(S, NodesCoord)
        (A, AFree, AFixed) = S.Initial.EquilibriumMatrix(S, ElementsCos)

        S.Initial.SVD.SVDEquilibriumMatrix(S, AFree)
        # success  = (AFree == A_free_answer).all()
        print(S.Initial.SVD.Um_free_row)  # analysis of the mechanism
        self.assertEqual(True, True)

    def test_SVDEquilibriumMatrix_ExperimentalSimplex(self):
        S = StructureObj()

        NodesCoord = np.array([[0.00, - 2043.8, 0.00],
                               [0.00, 0.00, 0.00],
                               [1770.00, - 1021.9, 0.00],
                               [590.00, - 2201.9,1950.00],
                               [-431.9,- 431.9, 1950.00],
                               [1611.9,- 431.9,1950.00]])
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
        IsDOFfree = np.array([False, True, False,
                              False, False, False,
                              True, True, False,
                              True, True, True,
                              True, True, True,
                              True, True, True])

        S.InitialData(NodesCoord, ElementsEndNodes, IsDOFfree)
        (l, ElementsCos) = S.Initial.ElementsLengthsAndCos(S, NodesCoord)
        (A, AFree, AFixed) = S.Initial.EquilibriumMatrix(S, ElementsCos)

        S.Initial.SVD.SVDEquilibriumMatrix(S, AFree)
        # success  = (AFree == A_free_answer).all()
        print(S.Initial.SVD.Um_free_row)  # analysis of the mechanism
        self.assertEqual(True, True)

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
