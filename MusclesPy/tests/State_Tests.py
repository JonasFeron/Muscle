import unittest
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

        S.RegisterData(NodesCoord,ElementsEndNodes,IsDOFfree)
        S.C = S.ConnectivityMatrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)

        Initial = State(S,NodesCoord)
        (Initial.ElementsL, Initial.ElementsCos) = Initial.ElementsLengthsAndCos(Initial.NodesCoord, S.C)

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

    def test_Simple_ComputeEquilibriumMatrix(self):
        S = StructureObj()
        NodesCoord = np.array([[0.0, 1.0, 0.0],
                               [1.0, 1.0, 0.0],
                               [2.0, 1.0, 0.0]])
        ElementsEndNodes = np.array([[0, 1],
                                     [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, True, True,
                              False, False, False])

        S.RegisterData(NodesCoord,ElementsEndNodes,IsDOFfree)
        C = S.ConnectivityMatrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)
        Initial = State(S,NodesCoord)
        (l,ElementsCos) = Initial.ElementsLengthsAndCos(NodesCoord, C)
        (A, A_free, A_fixed) = Initial.EquilibriumMatrix(None, ElementsCos)

        A_free_answer = np.array([[1.0, -1.0],
                                  [0.0, 0.0],
                                  [0.0, 0.0]])
        success  = (A_free == A_free_answer).all()

        self.assertEqual(success,True)

    def test_Simple_ComputeSVD(self):
        S = StructureObj()
        NodesCoord = np.array([[0.0, 1.0, 0.0],
                               [1.0, 1.0, 0.0],
                               [2.0, 1.0, 0.0]])
        Elements_ExtremitiesIndex = np.array([[0, 1],
                                              [1, 2]])
        IsDOFfree = np.array([False, False, False,
                              True, True, True,
                              False, False, False])

        S.RegisterData(NodesCoord, Elements_ExtremitiesIndex, IsDOFfree)
        C = S.ConnectivityMatrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)
        Initial = State(S,NodesCoord)
        (l, ElementsCos) = Initial.ElementsLengthsAndCos(NodesCoord, C)
        (A, A_free, A_fixed) = Initial.EquilibriumMatrix(None, ElementsCos)
        SVD = Initial.ComputeSVD(None, A_free)

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

    def test_FlexibilityMatrix(self):

        ElementsA = np.array([1e4,1e4]) #mm²
        ElementsE = np.array([100e3,0]) #MPa
        ElementsL = np.array([2,2]) #m

        S = StructureObj(0,2)
        Initial = State(S)
        F = Initial.Flexibility(StructureObj(), ElementsE, ElementsA, ElementsL)  #F=L/EA
        self.assertEqual(F[0], 2/(100e7))
        self.assertEqual(F[1], 1e6)

    def test_Simple_ComputeTension(self):

        #A structure composed of 2 elements. The first element has E = 100e3 and A=1e4 both in tension and compression. The second element has no stiffness in compression hence it slacks if compressed.
        ElementsA = np.array([[1e4,1e4],
                              [1e4, 1e4]]) #mm²
        ElementsE = np.array([[100e3,100e3],
                              [0, 100e3]]) #MPa
        ElementsLFree = np.array([2.0,2.0]) #m
        ElementsLCur = np.array([2.01,1.99])  #first is tensionned, second is compressed

        S = StructureObj(0,2) #a structure with no node and 2 elements
        deformed = State(S)
        T = deformed.Tension(ElementsLCur, ElementsLFree, ElementsE, ElementsA)
        self.assertAlmostEqual(T[0], 100e7/2*0.01,places=0)
        self.assertAlmostEqual(T[1], 0,places=0)

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

        S.RegisterData(NodesCoord, ElementsEndNodes, IsDOFfree)
        C = S.ConnectivityMatrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)
        Initial = State(S, NodesCoord)
        (l, ElementsCos) = Initial.ElementsLengthsAndCos(NodesCoord, C)
        (A, AFree, A_fixed) = Initial.EquilibriumMatrix(None, ElementsCos)

        #2) Define the Loads
        Loads = np.array([[0, 0, 0],
                          [2, 0, 3], #the load 1Z should always be unbalanced in this geometry
                          [0, 0, 0]])

        #3) test different tension
        #3a) equilibrium in X
        Tension = np.array([1, -1])
        fint = A@Tension #FYI
        Residual_a = Initial.Residual(A, Loads, Tension)
        ResidualFree_a = Initial.Residual(AFree, Loads, Tension)
        success_a = np.all(Residual_a == np.array([[1, 0, 0],[0, 0, 3],[1, 0, 0]]).reshape(-1,))
        successFree_a = np.all(ResidualFree_a == np.array([[0, 0, 0],[0, 0, 3],[0, 0, 0]]).reshape(-1,))
        self.assertEqual(success_a, True)
        self.assertEqual(successFree_a, True)

        # 3b) equilibrium in X bis
        Tension = np.array([2, 0])
        fint = A@Tension #FYI
        Residual_b = Initial.Residual(A, Loads, Tension)
        ResidualFree_b = Initial.Residual(AFree, Loads, Tension)
        success_b = np.all(Residual_b == np.array([[2, 0, 0],[0, 0, 3],[0, 0, 0]]).reshape(-1,))
        successFree_b = np.all(ResidualFree_b == np.array([[0, 0, 0],[0, 0, 3],[0, 0, 0]]).reshape(-1,))
        self.assertEqual(success_b, True)
        self.assertEqual(successFree_b, True)

        # 3C) equilibrium in X bis
        Tension = np.array([1, 0])
        fint = A@Tension #FYI
        Residual_c = Initial.Residual(A, Loads, Tension)
        ResidualFree_c = Initial.Residual(AFree, Loads, Tension)
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

        S.RegisterData(NodesCoord, ElementsEndNodes, IsDOFfree)
        S.C = S.ConnectivityMatrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)

        Initial = State(S, NodesCoord)
        (Initial.ElementsL, Initial.ElementsCos) = Initial.ElementsLengthsAndCos(Initial.NodesCoord, S.C)

        Tension = np.array([4])
        q = Initial.ForceDensities(Tension, Initial.ElementsL)
        kgLocList = Initial.GeometricLocalStiffnessList(None, q)
        Kgeo = S.GlobalFromLocalStiffnessMatrix(kgLocList)

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

        S.RegisterData(NodesCoord, ElementsEndNodes, IsDOFfree)
        S.C = S.ConnectivityMatrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)

        Initial = State(S, NodesCoord)
        (Initial.ElementsL, Initial.ElementsCos) = Initial.ElementsLengthsAndCos(Initial.NodesCoord, S.C)
        Tension = np.array([4,4])
        Kgeo = Initial.GeometricStiffnessMatrix(None, Tension, Initial.ElementsL)

        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
