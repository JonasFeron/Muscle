import numpy as np

def ReadDataFile(path):
    f = open(path, "r")
    key = f.readline()
    l = len(key) #should be equal to 36 but it equals to 37 due to unwanted space at the end
    # for i, c in enumerate(key):
    #     print(f"{i} {c}")

    Data_str = f.readlines()
    f.close()
    return (key[:l-1],Data_str)

class SharedData():
    def __init__(Data,TypeName,
                 NodesCoord,
                 ElementsEndNodes,
                 IsDOFfree,
                 ElementsType=[],
                 ElementsA=[],
                 ElementsE=[],
                 ElementsLFreeInit=[],
                 LoadsInit=[],
                 TensionInit=[],
                 ReactionsInit=[],
                 LoadsToApply=[],
                 LengtheningsToApply=[],
                 Residual0Threshold=0.0001,
                 Dt=0.01,
                 AmplMass=1,
                 MinMass=0.005,
                 MaxTimeStep=10000,
                 MaxKEReset=1000,
                 n_steps=1,
                 DynamicMass=[],
                 MaxFreqWanted = 0):
        """
        Initialize all the properties of a SharedData Object. A SharedData Object is an object that contains the same data in C# than in Python in order to communicate between the two languages via a file.txt encrypted in json format.
        Note that sharing Data is a task expensive in time (data are converted to a string which is printed and read).
        Therefore : only share the minimum amount of informations and recalculate other data if necessary.
        """
        Data.TypeName = TypeName #SharedData

        ##### Required Input From C# #####
        #input arguments from C# are lists which are converted in numpy.array
        Data.NodesCoord = np.array(NodesCoord) #[m] - shape (NodesCount, 3) - Coordinates must be in m otherwise: K matrix is in N/mm and it is too small)
        Data.ElementsEndNodes = np.array(ElementsEndNodes, dtype=int)
        Data.IsDOFfree = np.array(IsDOFfree, dtype=bool)
        Data.ElementsType = np.array(ElementsType, dtype=int).reshape((-1,)) # -1 for struts, +1 for cables
        Data.ElementsA = np.array(ElementsA).reshape((-1,2)) #[mm²] - [AreaInCompression, AreaInTension]
        Data.ElementsE = np.array(ElementsE).reshape((-1,2)) #[MPa] - [EInCompression, EInTension]
        Data.ElementsLFreeInit = np.array(ElementsLFreeInit).reshape((-1,)) #[m] - The free lengths before the Lengthenings are applied
        Data.LoadsInit = np.array(LoadsInit).reshape((-1,))
        Data.TensionInit = np.array(TensionInit).reshape((-1,))
        Data.ReactionsInit = np.array(ReactionsInit).reshape((-1,))
        Data.LoadsToApply = np.array(LoadsToApply).reshape((-1,))
        Data.LengtheningsToApply = np.array(LengtheningsToApply).reshape((-1,))
        Data.Residual0Threshold = Residual0Threshold

        #Data for the Dynamic Relaxation method
        Data.Dt = Dt
        Data.AmplMass = AmplMass
        Data.MinMass = MinMass
        Data.MaxTimeStep = MaxTimeStep
        Data.MaxKEReset = MaxKEReset

        #Data for the Non-Linear displacement method
        Data.n_steps = n_steps

        #Data for the dynamic computation module
        Data.DynamicMass = DynamicMass
        Data.MaxFreqWanted = MaxFreqWanted #Put at 0 as default value (if nothing is inputed. It will send all the frequencies and modes.)

def ToSharedDataObject(dct):
    """
    Function that takes in a dictionary and returns a custom object SharedData associated to the dict.
    """
    if 'SharedData' in dct.values():
        return SharedData(**dct) #call the constructor of SharedData with all the values of the dictionnary. The Name of the properties in Python must match with the ones in CSharp !!
    return dct


