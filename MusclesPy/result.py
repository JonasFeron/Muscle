import json
from StructureObj import StructureObj
import os

File_Test_Result = "Test_Result.txt"
FileDRResult = "DynamicRelaxationResult.txt"
File_Assemble_Result = "Assemble_Result.txt"
File_LinearSolve_Result = "LinearSolve_Result.txt"
File_NonLinearSolve_Result = "NonLinearSolve_Result.txt"


def WriteResultFile(dataPath,resultFileName,key,result):
    dir = os.path.dirname(dataPath)
    file = os.path.join(dir,resultFileName)
    f = open(file, "w")
    f.writelines([key,"\n",result])
    f.close()
    return file




class SharedAssemblyResult():
    def __init__(Answ):
        """
        initialise empty SharedAssemblyResult
        Note that sharing data is a task expensive in time (data are converted to a string which is printed and read).
        Therefore : only share the minimum amount of informations and recalculate other data if necessary.
        """
        Answ.TypeName = "SharedAssemblyResult"
        Answ.C = []
        Answ.Km = []
        Answ.Km_free = []
        Answ.A = []
        Answ.A_free = []

        Answ.S = []
        Answ.r = 0
        Answ.Sr = []

        Answ.s = 0
        Answ.Vr_row = []
        Answ.Vs_row = []
        Answ.SS = []

        Answ.m = 0
        Answ.Ur_row = []
        Answ.Ur_free_row = []
        Answ.Um_row = []
        Answ.Um_free_row = []

    def PopulateWith(Answ,S0):
        if isinstance(S0,StructureObj):
            if S0.NodesCount<=10: #it may be interesting to analyze the matrices of small structures
                Answ.C = S0.C.tolist()
                Answ.Km = S0.Km.round(4).tolist()
                Answ.Km_free = S0.Km_free.round(4).tolist()
                Answ.A = S0.A.round(4).tolist()
                Answ.A_free = S0.AFree.round(4).tolist()

                Answ.S = S0.SVD.S.round(4).tolist()
                Answ.r = int(S0.SVD.r)
                Answ.Sr = S0.SVD.Sr.round(4).tolist()

                Answ.s = int(S0.SVD.s)
                Answ.Vr_row = S0.SVD.Vr_row.round(4).tolist()
                Answ.Vs_row = S0.SVD.Vs_row.round(4).tolist()
                Answ.SS = S0.SVD.SS.round(4).tolist()

                Answ.m = int(S0.SVD.m)
                Answ.Ur_row = S0.SVD.Ur_row.round(4).tolist()
                Answ.Ur_free_row = S0.SVD.Ur_free_row.round(4).tolist()
                Answ.Um_row = S0.SVD.Um_row.round(4).tolist()
                Answ.Um_free_row = S0.SVD.Um_free_row.round(4).tolist()
            else :
                Answ.S = S0.SVD.S.round(4).tolist()
                Answ.r = int(S0.SVD.r)
                Answ.s = int(S0.SVD.s)
                Answ.SS = S0.SVD.SS.round(4).tolist() #self-stress modes

                Answ.m = int(S0.SVD.m)
                Answ.Um_row = S0.SVD.Um_row.round(4).tolist() #mechanisms

        # ##### Calculation Datas #####
        # Answ.n_it
        #
        # Answ.Loads_Already_Applied
        # Answ.Displacements_Already_Applied
        # Answ.Reactions_Already_Applied

        #
        #
        # Answ.AxialForces_To_Apply
        #
        # ##### Calculation Results #####
        # Answ.Displacements_Results
        # Answ.Displacements_Results_Total
        # Answ.Reactions_Results
        # Answ.Reactions_Results_Total
        # Answ.AxialForces_Results


class SharedAssemblyResultEncoder(json.JSONEncoder):
    """
    La classe SharedAssemblyResultEncoder permet d'enregistrer toutes les propriétés d'un object SharedAssemblyResult dans un dictionnaire et les envoyer à C#
    """
    def default(self, obj):
        if isinstance(obj, SharedAssemblyResult):
            return obj.__dict__ # obj.__dct__ = {'property': value, ...}
        else : # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)


class SharedSolverResult():
    def __init__(Answ):
        """
        initialize empty SharedSolverResult
        Note that sharing data is a task expensive in time (data are converted to a string which is printed and read).
        Therefore : only share the minimum amount of informations and recalculate other data if necessary.
        """
        Answ.TypeName = "SharedSolverResult"

        # ##### Solve informations #####
        Answ.NodesCoord = []
        Answ.Loads = []
        Answ.Tension = []
        Answ.Reactions = []
        Answ.ElementsLFree = []  # Lengths of the elements when the elements are free of any tension, or in other words, when the structure is disassemble.

        Answ.Residual = []  # the unbalanced loads
        Answ.IsInEquilibrium = False  # the final state of the structure is in equilibrum if the unbalanced loads (Residual) are below a certain threshold (very small)

        #Specific to DR method
        Answ.nTimeStep = 0
        Answ.nKEReset = 0


    def PopulateWith(Answ, Struct):
        if isinstance(Struct, StructureObj):
            Answ.NodesCoord = Struct.Final.NodesCoord.round(8).tolist() #[m] - shape (3NodesCount,)
            Answ.Loads = Struct.Final.Loads.round(5).tolist() #[N] - shape (3NodesCount,)
            Answ.Tension = Struct.Final.Tension.round(5).tolist() #[N] - shape (ElementsCount,)
            Answ.Reactions = Struct.Final.Reactions.round(5).tolist() #[N] - shape (FixationsCount,)
            Answ.ElementsLFree = Struct.Final.ElementsLFree.round(8).tolist() #[m] - shape (ElementsCount,)

            Answ.Residual = Struct.Final.Residual.round(5).tolist() #[N] - shape (3NodesCount,)
            Answ.IsInEquilibrium = Struct.Final.IsInEquilibrium

            Answ.nTimeStep = Struct.DR.nTimeStep
            Answ.nKEReset = Struct.DR.nKEReset


class SharedSolverResultEncoder(json.JSONEncoder):
    """
    La classe SharedSolverResultEncoder permet d'enregistrer toutes les propriétés d'un object SharedSolverResult dans un dictionnaire et les envoyer à C#
    """
    def default(self, obj):
        if isinstance(obj, SharedSolverResult):
            return obj.__dict__ # obj.__dct__ = {'property': value, ...}
        else : # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)


# class SharedSolverResult():
#     def __init__(Answ):
#         """
#         initialise empty SharedSolverResult
#         Note that sharing data is a task expensive in time (data are converted to a string which is printed and read).
#         Therefore : only share the minimum amount of informations and recalculate other data if necessary.
#         """
#         Answ.TypeName = "SharedSolverResult"
#         # Answ.K_constrained = []  # required to solve the structure with imposed displacements of the supports
#
#         # ##### Solve informations #####
#         Answ.Stages = []
#
#         # Answ.Loads_Already_Applied = np.zeros((Answ.NodesCount,3))
#         # Answ.LoadsToApply = np.zeros((Answ.NodesCount, 3))
#         # Answ.Loads_Applied = np.zeros((Answ.NodesCount, 3)) # results of Stages*LoadsToApply
#         # Answ.Loads_Total = np.zeros((Answ.NodesCount, 3)) # Already_Applied + To_Apply
#
#         # Answ.TensionInit = np.zeros((Answ.ElementsCount,)) #considered in Geometric stiffness
#         Answ.AxialForces_Results = [] # [N] #results from LoadsToApply
#         # Answ.AxialForces_Total = np.zeros((Answ.ElementsCount,)) # Results + Already_Applied
#
#         # Answ.Displacements_Already_Applied = np.zeros((Answ.NodesCount,3)) # this is such that this.NodesCoord = NodesCoord0 + this.Displacements_Already_Applied. If the structure is solved for the first time,Displacements_Already_Applied =0.
#         Answ.Displacements_Results = [] #[mm] #results from LoadsToApply
#         # Answ.Displacements_Total = np.zeros((Answ.NodesCount, 3)) # Results + Already_Applied
#
#         # Answ.Reactions_Already_Applied = np.zeros((Answ.FixationsCount,))
#         Answ.Reactions_Results = [] #[N] #results from LoadsToApply
#         # Answ.Reactions_Total = np.zeros((Answ.FixationsCount,)) # Results + Already_Applied
#
#     def PopulateWith(Answ,S0):
#         if isinstance(S0,StructureObj):
#             Answ.Stages=S0.Stages.round(5).tolist()
#             Answ.AxialForces_Results = S0.AxialForces_Results.round(2).tolist()
#             Answ.Displacements_Results = S0.Displacements_Results.round(5).tolist()
#             Answ.Reactions_Results = S0.Reactions_Results.round(2).tolist()
#             # if DR.NodesCount<=10: #it may be interesting to analyze the matrices of small structures
#
#
# class SharedSolverResultEncoder(json.JSONEncoder):
#     """
#     La classe SharedSolverResultEncoder permet d'enregistrer toutes les propriétés d'un object SharedSolverResult dans un dictionnaire et les envoyer à C#
#     """
#     def default(self, obj):
#         if isinstance(obj, SharedSolverResult):
#             return obj.__dict__ # obj.__dct__ = {'property': value, ...}
#         else : # Let the base class default method raise the TypeError
#             return json.JSONEncoder.default(self, obj)
