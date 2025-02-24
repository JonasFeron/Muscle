import numpy as np


class Twin_Elements:
    def __init__(self, type=None, end_nodes=None, areas=None, young_moduli=None, initial_free_lengths=None):
        """Python equivalent of C# Twin_Elements class"""

        # inputs from C#
        self.type = np.array([], dtype=int)   # [-] - shape (ElementsCount, ) - Type of the Elements : -1 for struts, 1 for cables
        self.end_nodes = np.array([[],[]], dtype=int)  # [-] - shape (ElementsCount, 2) - indices of the end nodes 
        self.areas = np.array([[],[]], dtype=float)  # [mm²] - shape (ElementsCount, 2) - Area in Compression and Area in Tension of the Elements
        self.young_moduli = np.array([[],[]], dtype=float) # [MPa] - shape (ElementsCount, 2) - Young Moduli in Compression and in Tension of the Elements
        self.initial_free_lengths = np.array([], dtype=float) # shape (ElementsCount, ) - Free Length of the Elements before any analysis

        #additionnal deduced attributes
        self.count = 0 # number of elements

        self.initialize(type, end_nodes, areas, young_moduli, initial_free_lengths)



### private methods ###

    def initialize(self, type, end_nodes, areas, young_moduli, initial_free_lengths):
        """Initialize Twin_Elements with given parameters.
        Args can be either None, Python lists (from C#), or numpy arrays (from Python)
        """
        # Handle end_nodes first to establish count
        if end_nodes is not None:
            self.end_nodes = end_nodes if isinstance(end_nodes, np.ndarray) else np.array(end_nodes, dtype=int)
            self.count = len(self.end_nodes)
            assert self.end_nodes.shape == (self.count, 2), f"end_nodes should have shape ({self.count}, 2) but got {self.end_nodes.shape}"
        else:
            self.end_nodes = np.array([], dtype=int).reshape((0, 2))
            self.count = 0

        # Handle other arrays with size assertions
        if type is not None:
            self.type = type if isinstance(type, np.ndarray) else np.array(type, dtype=int)
            assert len(self.type) == self.count, f"type should have length {self.count} but got {len(self.type)}"
        else:
            self.type = np.array([], dtype=int)
        
        if areas is not None:
            self.areas = areas if isinstance(areas, np.ndarray) else np.array(areas, dtype=float)
            assert self.areas.shape == (self.count, 2), f"areas should have shape ({self.count}, 2) but got {self.areas.shape}"
        else:
            self.areas = np.array([], dtype=float).reshape((0, 2))
        
        if young_moduli is not None:
            self.young_moduli = young_moduli if isinstance(young_moduli, np.ndarray) else np.array(young_moduli, dtype=float)
            assert self.young_moduli.shape == (self.count, 2), f"young_moduli should have shape ({self.count}, 2) but got {self.young_moduli.shape}"
        else:
            self.young_moduli = np.array([], dtype=float).reshape((0, 2))
        
        if initial_free_lengths is not None:
            self.initial_free_lengths = initial_free_lengths if isinstance(initial_free_lengths, np.ndarray) else np.array(initial_free_lengths, dtype=float)
            assert len(self.initial_free_lengths) == self.count, f"initial_free_lengths should have length {self.count} but got {len(self.initial_free_lengths)}"
        else:
            self.initial_free_lengths = np.array([], dtype=float)



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

    #     if isinstance(ElementsEndNodes, np.ndarray):
    #         Self.ElementsEndNodes = ElementsEndNodes.reshape(-1, 2).astype(int)
    #         Self.ElementsCount = Self.ElementsEndNodes.shape[0]
    #     else:
    #         Self.ElementsEndNodes = None
    #         Self.ElementsCount = -1

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


    #     if isinstance(ElementsType, np.ndarray) and ElementsType.size == Self.ElementsCount:
    #         Self.ElementsType = ElementsType.reshape((-1,)).astype(int) #-1 if struts, +1 if cables
    #     else:
    #         Self.ElementsType = -np.ones((Self.ElementsCount,)) #all struts

    #     if isinstance(ElementsA, np.ndarray) and ElementsA.size == 2*Self.ElementsCount:
    #         Self.ElementsA = ElementsA.reshape((-1, 2)) #[AinCompression,AinTension]
    #     elif isinstance(ElementsA, np.ndarray) and ElementsA.size == 1*Self.ElementsCount:
    #         AinTensionAndCompression = ElementsA.reshape((-1, 1))
    #         Self.ElementsA = np.hstack((AinTensionAndCompression,AinTensionAndCompression))
    #     else:
    #         Self.ElementsA = None

    #     if isinstance(ElementsE, np.ndarray) and ElementsE.size == 2*Self.ElementsCount:
    #         Self.ElementsE = ElementsE.reshape((-1, 2)) #[EinCompression,EinTension]
    #     elif isinstance(ElementsE, np.ndarray) and ElementsE.size == 1*Self.ElementsCount:
    #         EinTensionAndCompression = ElementsE.reshape((-1, 1))
    #         Self.ElementsE = np.hstack((EinTensionAndCompression,EinTensionAndCompression))
    #     else:
    #         Self.ElementsE = None




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




    #     if isinstance(LoadsToApply, np.ndarray) and LoadsToApply.size == 3 * Self.NodesCount:
    #         Self.LoadsToApply = LoadsToApply.reshape(-1,)
    #     else:
    #         Self.LoadsToApply = np.zeros((3 * Self.NodesCount,))


    #     if isinstance(LengtheningsToApply, np.ndarray) and LengtheningsToApply.size == Self.ElementsCount:
    #         Self.LengtheningsToApply = LengtheningsToApply.reshape(-1, )
    #     else:
    #         Self.LengtheningsToApply = np.zeros((Self.ElementsCount,))

    #     if Residual0Threshold > 0:
    #         Self.Residual0Threshold=Residual0Threshold
    #     else:
    #         Self.Residual0Threshold=0.00001

    #     if n_steps >=1:
    #         Self.n_steps=n_steps
    #     else:
    #         Self.n_steps=1



