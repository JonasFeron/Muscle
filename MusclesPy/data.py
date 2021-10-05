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
    def __init__(Data,TypeName,NodesCoord,Elements_ExtremitiesIndex, IsDOFfree, Elements_A=[], Elements_E=[], AxialForces_Already_Applied=[], Loads_To_Apply=[],n_steps=1):
        """
        initialise tous les attributs de l'objet SharedData
        Note that sharing Data is a task expensive in time (data are converted to a string which is printed and read).
        Therefore : only share the minimum amount of informations and recalculate other data if necessary.
        """
        Data.TypeName = TypeName

        ##### Required Input From C# #####
        #input arguments from C# are lists which are converted in numpy.array
        Data.NodesCoord = np.array(NodesCoord) #in m (it must be in m otherwise: K matrix is in N/mm and it is too small)
        Data.Elements_ExtremitiesIndex = np.array(Elements_ExtremitiesIndex, dtype=int)
        Data.IsDOFfree = np.array(IsDOFfree, dtype=bool)
        Data.Elements_A = np.array(Elements_A) #data are in mm²
        Data.Elements_E = np.array(Elements_E) #data are in MPa
        Data.AxialForces_Already_Applied = np.array(AxialForces_Already_Applied)
        Data.Loads_To_Apply = np.array(Loads_To_Apply) #Note that Loads to Apply already contain the axialforces to Apply as PointLoads
        Data.n_steps = n_steps

        # ##### Calculation Datas #####
        # Data.n_it
        #
        # Data.Loads_Already_Applied
        # Data.Displacements_Already_Applied
        # Data.Reactions_Already_Applied

        #
        #
        # Data.AxialForces_To_Apply
        #
        # ##### Calculation Results #####
        # Data.Displacements_Results
        # Data.Displacements_Results_Total
        # Data.Reactions_Results
        # Data.Reactions_Results_Total
        # Data.AxialForces_Results

def ToSharedDataObject(dct):
    """
    Function that takes in a dictionary and returns a custom object SharedData associated to the dict.
    """
    if 'SharedData' in dct.values():
        return SharedData(**dct) #call the constructor of SharedData with all the values of the dictionnary. The properties must be in the same order than in CSharp !!
    return dct


