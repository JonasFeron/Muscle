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
        S.C = S.Connectivity_Matrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)

        Initial = State(S,NodesCoord)
        (Initial.ElementsL, Initial.ElementsCos) = Initial.ComputeElementsLengthsAndCos(Initial.NodesCoord, S.C)

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
        C = S.Connectivity_Matrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)
        Initial = State(S,NodesCoord)
        (l,ElementsCos) = Initial.ComputeElementsLengthsAndCos(NodesCoord,C)
        (A, A_free, A_fixed) = Initial.ComputeEquilibriumMatrix(C,IsDOFfree,ElementsCos)

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
        C = S.Connectivity_Matrix(S.NodesCount, S.ElementsCount, S.ElementsEndNodes)
        Initial = State(S,NodesCoord)
        (l, ElementsCos) = Initial.ComputeElementsLengthsAndCos(NodesCoord,C)
        (A, A_free, A_fixed) = Initial.ComputeEquilibriumMatrix(C,IsDOFfree,ElementsCos)
        SVD = Initial.ComputeSVD(A_free)

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

    def test_Simple_ComputeTension(self):

        #A structure composed of 2 elements. The first element has E = 100e3 and A=1e4 both in tension and compression. The second element has no stiffness in compression hence it slacks if compressed.
        ElementsA = np.array([[1e4,1e4],
                              [1e4, 1e4]]) #mm²
        ElementsE = np.array([[100e3,100e3],
                              [0, 100e3]]) #MPa
        ElementsLFree = np.array([2.0,2.0]) #m
        ElementsLCur = np.array([2.1,1.9])  #first is tensionned, second is compressed

        S = StructureObj(0,2) #a structure with no node and 2 elements
        deformed = State(S)
        T = deformed.ComputeTension(ElementsLFree,ElementsLCur)
        self.assertEqual(T[0], 100e7/2*0.1)
        self.assertEqual(T[1], 0)


if __name__ == '__main__':
    unittest.main()
