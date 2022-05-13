import json
from StructureObj import StructureObj
import os
import numpy as np

FileTestResult = "TestResult.txt"
FileDRResult = "DynamicRelaxationResult.txt"
FileAssembleResult = "AssembleResult.txt"
FileLinearSolveResult = "LinearSolveResult.txt"
FileNonLinearSolveResult = "NonLinearSolveResult.txt"
FileDynamicResult = "DynamicResult.txt"

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

        Answ.A = []
        Answ.AFree = []

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

    def PopulateWith(Answ, Struct):
        if isinstance(Struct, StructureObj):
            if Struct.NodesCount<=10: #it may be interesting to analyze the matrices of small structures
                Answ.C = Struct.C.tolist()

                Answ.A = Struct.Initial.A.round(4).tolist()
                Answ.AFree = Struct.Initial.AFree.round(4).tolist()

                Answ.S = Struct.Initial.SVD.S.round(4).tolist()
                Answ.r = int(Struct.Initial.SVD.r)
                Answ.Sr = Struct.Initial.SVD.Sr.round(4).tolist()

                Answ.s = int(Struct.Initial.SVD.s)
                Answ.Vr_row = Struct.Initial.SVD.Vr_row.round(4).tolist()
                Answ.Vs_row = Struct.Initial.SVD.Vs_row.round(4).tolist()
                Answ.SS = Struct.Initial.SVD.SS.round(6).tolist()

                Answ.m = int(Struct.Initial.SVD.m)
                Answ.Ur_row = Struct.Initial.SVD.Ur_row.round(4).tolist()
                Answ.Ur_free_row = Struct.Initial.SVD.Ur_free_row.round(4).tolist()
                Answ.Um_row = Struct.Initial.SVD.Um_row.round(6).tolist()
                Answ.Um_free_row = Struct.Initial.SVD.Um_free_row.round(4).tolist()
            else :
                Answ.S = Struct.Initial.SVD.S.round(4).tolist()
                Answ.r = int(Struct.Initial.SVD.r)
                Answ.s = int(Struct.Initial.SVD.s)
                Answ.SS = Struct.Initial.SVD.SS.round(4).tolist() #self-stress modes

                Answ.m = int(Struct.Initial.SVD.m)
                Answ.Um_row = Struct.Initial.SVD.Um_row.round(4).tolist() #mechanisms

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
            Answ.NodesCoord = Struct.Final.NodesCoord.round(8).reshape((-1,3)).tolist() #[m] - shape (NodesCount,3)
            Answ.Loads = Struct.Final.Loads.round(5).reshape((-1,3)).tolist() #[N] - shape (NodesCount,3)
            Answ.Tension = Struct.Final.Tension.round(5).tolist() #[N] - shape (ElementsCount,)
            Answ.Reactions = Struct.Final.Reactions.round(5).tolist() #[N] - shape (FixationsCount,)
            Answ.ElementsLFree = Struct.Final.ElementsLFree.round(8).tolist() #[m] - shape (ElementsCount,)

            Answ.Residual = Struct.Final.Residual.round(5).reshape((-1,3)).tolist() #[N] - shape (NodesCount,3)
            Answ.IsInEquilibrium = bool(Struct.Final.IsInEquilibrium)

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

class SharedSolverResult_dynamics():
    def __init__(Answ):
        """

        """
        Answ.TypeName = "SharedSolverResultDynamics"

        # ##### Solve informations #####
        Answ.NumberOfFrequency = 0
        Answ.Frequency = []
        Answ.Modes =  []
        Answ.TotMode = []

    def PopulateWith_Dynamics(Answ,Struct): #For the dynamics part
        if isinstance(Struct, StructureObj):
            Answ.NumberOfFrequency = 2 #Struct.NFreq
            #Answ.Frequency = Struct.freq.round(5).reshape((-1,)).tolist() #Frequencies [Hz] who are ranked 
            Answ.Frequency = np.array([1,2,3])
            Answ.Frequency = Answ.Frequency.round(5).reshape((-1,)).tolist()
            
            
            #Struct.mode = Struct.mode.T #Need to transpose because the \Phi matrix has each mode writen vertically
            #The reshape depends on the number of frequency asked by the user
            Struct.mode = np.array([[1,2,3],[1,4,5],[6,7,8]])
            Struct.mode = Struct.mode.T
            Answ.Modes = Struct.mode.round(5).reshape((3,3)).tolist()
            #Shape = Struct.mode.shape
            #Answ.Modes = Struct.mode.round(5).reshape((Shape[0],Shape[1])).tolist() #Modes ranked as the frequencies
            
            Struct.TotMode = np.array([[1,2,3],[1,4,5],[6,7,8]])
            Struct.TotMode = Struct.TotMode.T
            Answ.TotMode = Struct.TotMode.round(5).reshape((3,3)).tolist()
            #Struct.TotMode = Struct.TotMode.T
            #Shape = Struct.TotMode.shape
            #Answ.TotMode = Struct.TotMode.round(5).reshape((Shape[0],Shape[1])).tolist()

            #Answ.TotMode = Struct.TotMode.round(5).reshape((Struct.DOFfreeCount,3*Struct.NodesCount)).tolist()
            #Both reshape are working --> tested in python
            #Round : number of digit after the comma
            #Reshape also work : obtain a list containing DOFfreeCount lists of arrays containint DOFfreeCount elements

class SharedSolverResult_dynamicsEncoder(json.JSONEncoder):
    """
    La classe SharedSolverResultEncoder permet d'enregistrer toutes les propriétés d'un object SharedSolverResult dans un dictionnaire et les envoyer à C#
    """
    def default(self, obj):
        if isinstance(obj, SharedSolverResult_dynamics):
            return obj.__dict__ # obj.__dct__ = {'property': value, ...}
        else : # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)


