import numpy as np


class Twin_Nodes:
    def __init__(self, coordinates=None, dof=None):
        """Python equivalent of C# Twin_Nodes class"""
        self.coordinates = np.array([], dtype=float).reshape((0, 3))        # Nodal coordinates - shape (NodesCount, 3)

        # Supports
        self.dof = np.array([], dtype=bool).reshape((0, 3))   # [bool] - shape (3NodesCount,). Each DegreeOfFreedom can be fixed (False) or free (True). Each point i is associated to its X DOF (3i), Y DOF (3i+1), Z DOF (3i+2). 
        
        #additionnal deduced attributes
        self.count = 0 # number of elements

        self.initialize(type, coordinates, dof)



### private methods ###

    def initialize(self, coordinates, dof):
        """Initialize Twin_Elements with given parameters.
        Args can be either None, Python lists (from C#), or numpy arrays (from Python)
        """
        # Handle coordinates first to establish count
        if coordinates is not None:
            self.coordinates = coordinates if isinstance(coordinates, np.ndarray) else np.array(coordinates, dtype=float)
            self.count = len(self.coordinates)
            assert self.coordinates.shape == (self.count, 3), f"coordinates should have shape ({self.count}, 3) but got {self.coordinates.shape}"
        else:
            self.coordinates = np.array([], dtype=float).reshape((0, 3))
            self.count = 0

        # Handle other arrays with size assertions
        if dof is not None:
            self.dof = dof if isinstance(dof, np.ndarray) else np.array(dof, dtype=bool)
            assert self.dof.shape == (self.count, 3), f"dof should have shape ({self.count}, 3) but got {self.dof.shape}"
        else:
            self.dof = np.array([], dtype=bool).reshape((0, 3))
        



    # def InitialData(Self, NodesCoord, ElementsEndNodes, IsDOFfree, ElementsType=np.zeros((0,)), ElementsA=np.zeros((0, 2)),
    #                 ElementsE=np.zeros((0, 2)), ElementsLfreeInit = -1, LoadsInit=np.zeros((0,)),
    #                 TensionInit=np.zeros((0,)), ReactionsInit=np.zeros((0,)), LoadsToApply=np.zeros((0,)),
    #                 LengtheningsToApply=np.zeros((0,)), Residual0Threshold=0.00001, n_steps=1):

    #     ### Initialize fundamental datas ###
    #     if isinstance(NodesCoord, np.ndarray):
    #         Self.NodesCount = NodesCoord.reshape(-1, 3).shape[0]
    #         Self.Initial.NodesCoord = NodesCoord.reshape(-1, ) #see StateInitial
    #     else:
    #         Self.Initial.NodesCoord = None
    #         Self.NodesCount = -1


    #     if isinstance(IsDOFfree, np.ndarray):
    #         Self.IsDOFfree = IsDOFfree.reshape((-1,)).astype(bool)
    #         Self.DOFfreeCount = np.sum(np.ones(3 * Self.NodesCount, dtype=int)[Self.IsDOFfree])
    #         Self.FixationsCount = 3 * Self.NodesCount - Self.DOFfreeCount
    #     else:
    #         Self.IsDOFfree = None
    #         Self.FixationsCount = -1
    #         Self.DOFfreeCount = -1

    #     ### Initialize optional datas ###
    #     Self.C = Self.ConnectivityMatrix(Self.NodesCount,Self.ElementsCount,Self.ElementsEndNodes)
    #     (Self.Initial.ElementsL, Self.Initial.ElementsCos) = Self.Initial.ElementsLengthsAndCos(Self,Self.Initial.NodesCoord)  # thus calculate the free lengths based on the nodes coordinates





    #     if isinstance(LoadsInit, np.ndarray) and LoadsInit.size == 3 * Self.NodesCount:
    #         Self.Initial.Loads = LoadsInit.reshape(-1, )
    #     else:
    #         Self.Initial.Loads = np.zeros((3 * Self.NodesCount,))


    #     if isinstance(TensionInit, np.ndarray) and TensionInit.size == Self.ElementsCount:
    #         Self.Initial.Tension = TensionInit.reshape((-1,))
    #     else:
    #         Self.Initial.Tension = np.zeros((Self.ElementsCount,))


    #     if isinstance(ReactionsInit, np.ndarray) and ReactionsInit.size == Self.FixationsCount:
    #         Self.Initial.Reactions = ReactionsInit.reshape(-1, )
    #     else:
    #         Self.Initial.Reactions = np.zeros((Self.FixationsCount,))




    #     if Self.ElementsE.shape == (Self.ElementsCount,2):
    #         Self.Initial.ElementsE = Self.ElementsInTensionOrCompression(Self.Initial.Tension,Self.ElementsE)
    #     if Self.ElementsA.shape == (Self.ElementsCount,2):
    #         Self.Initial.ElementsA = Self.ElementsInTensionOrCompression(Self.Initial.Tension,Self.ElementsA)


    #     if isinstance(ElementsLfreeInit, np.ndarray) and ElementsLfreeInit.size == Self.ElementsCount:
    #         Self.Initial.ElementsLFree = ElementsLfreeInit.reshape((-1,))
    #     else:
    #         Self.Initial.ElementsLFree = -np.ones((Self.ElementsCount,))

    #     if (Self.Initial.ElementsLFree < np.zeros((Self.ElementsCount,))).any() or np.any(ElementsLfreeInit == -1):  # if the free lengths are smaller than 0, it means they have not been calculated yet.
    #         if np.count_nonzero(np.around(Self.Initial.Tension,decimals = 6))>0 : # if some elements are pre-tensionned, make sure the free lengths take it into account
    #             F = Self.Flexibility(Self.Initial.ElementsE, Self.Initial.ElementsA, Self.Initial.ElementsL) #flexibility with initial length (considered infinite if EA is close to 0)
    #             EA = Self.Initial.ElementsL/F # stiffness EA of the elements (with zeros replaced by 1e-9)
    #             Init_strain = Self.Initial.Tension/EA
    #             Self.Initial.ElementsLFree = Self.Initial.ElementsL/(1+Init_strain)
    #         else : #there are no initial tension
    #             Self.Initial.ElementsLFree = Self.Initial.ElementsL.copy()  # thus calculate the free lengths based on the nodes coordinates





