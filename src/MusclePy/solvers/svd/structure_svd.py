from MusclePy.femodel.fem_nodes  import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.femodel.fem_structure import FEM_Structure
import numpy as np


class Structure_SVD(FEM_Structure):
    def __init__(self, nodes: FEM_Nodes, elements: FEM_Elements):
        """Initialize Structure_SVD, extending FEM_Structure with equilibrium matrix, and singular value decomposition method.
        
        Args:
            nodes: FEM_Nodes instance containing nodal data
            elements: FEM_Elements instance that must reference the same nodes instance
        """
        # Call parent class constructor
        super().__init__(nodes, elements)



    def EquilibriumMatrix(self, Struct, ElementsCos):
        """
        :param Struct:
        :return: Compute the equilibrium matrix of the structure in its current state based on the current cosinus director of the elements
        """
        #1) Check inputs
        dof = Struct.IsDOFfree
        C = Struct.C
        ElementsCount = Struct.ElementsCount
        NodesCount = Struct.NodesCount
        assert dof.size !=0 , "Please check the shape of the support condition IsDOFfree"
        assert ElementsCount != 0, "Please check the ElementsCount"
        assert NodesCount != 0, "Please check the NodesCount"

        CosX = ElementsCos[:, 0]
        CosY = ElementsCos[:, 1]
        CosZ = ElementsCos[:, 2]

        # 2) calculate equilibrium matrix
        # for each node (corresponding to one row), if the line (corresponding to a column) is connected to the node, then the entry of A contains the cos director, else 0.
        Ax = C.T @ np.diag(
            CosX)  # (NodesCount, ElementsCount)  =  (NodesCount, ElementsCount) @ (ElementsCount, ElementsCount)
        Ay = C.T @ np.diag(CosY)
        Az = C.T @ np.diag(CosZ)

        A = np.zeros((3 * NodesCount, ElementsCount))  # (3*nbr nodes, nbr lines)

        # the Degrees Of Freedom are sorted like this [0X 0Y OZ 1X 1Y 1Z ... (n-1)X (n-1)Y (n-1)Z]
        for i in range(NodesCount):
            A[3 * i, :] = Ax[i, :]
            A[3 * i + 1, :] = Ay[i, :]
            A[3 * i + 2, :] = Az[i, :]

        AFree = A[dof]  # (nbr free dof, ElementsCount)
        AFixed = A[~dof]  # (nbr fixed dof, ElementsCount)

        return (A, AFree, AFixed)

    def MaterialStiffnessMatrix(Cur, Struct, A, Flex):
        """
        Compute the material stiffness matrix of the structure in the current state given the equilibrium matrix and the flexibilities in the current state
        :param Struct: The StructureObject in the current state
        :param A: [/] - shape (3*NodesCount,ElementsCount) - The equilibrium matrix of the structure in the current state
        :param Flex: [m/N] - shape (ElementsCount,) - The flexibility vector L/EA for each element in the current state
        :return: Kmat : [N/m] - shape(3*NodesCount,3*NodesCount) - the material stiffness matrix of the structure in the current state
        """
        ElementsCount = Struct.ElementsCount
        NodesCount = Struct.NodesCount
        DOFfreeCount = Struct.DOFfreeCount

        assert A.shape == (3 * NodesCount, ElementsCount) or A.shape == (DOFfreeCount, ElementsCount), "Please check the shape of A"
        assert Flex.size == ElementsCount, "Please check the shape of the Flex vector"
        F = Flex.reshape(-1, )

        Kbsc = np.diag(1 / F)  # EA/L in a diagonal matrix. Note that EA/L can be equal to 0 if the cable is slacked
        B = A.T  # The compatibility matrix is the linear application which transforms the displacements into elongation.
        Kmat = A @ Kbsc @ B  # (3*NodesCount,3*NodesCount) OR (DOFfreeCount, DOFfreeCount)

        return Kmat
