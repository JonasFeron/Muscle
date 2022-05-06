import data as d
import result as r
from StructureObj import StructureObj
import sys
import json


def main(): # START READING FROM HERE

    # 1) retrieve inputs from Grasshopper/C#
    key = sys.argv[1] #the ID of the c# command executing this script. It allows to connect the command with the results
    dataPath = sys.argv[2] #the location and the name of the file.txt where the data are written by C#

    (keyInTxtFile,DataString) = d.ReadDataFile(dataPath) #Read the file.txt to collect data as a string

    output_str=" " # Initialize the output as a string

    if (key  == keyInTxtFile):
        try:
            output_str = core(DataString[0]) # See method core here below

        except Exception as e:
            output_str = str(e)
    else:
        output_str = "Keys from command prompt and Data text file did not match"

    resultPath = r.WriteResultFile(dataPath,r.FileDynamicResult,key,output_str)
    print(key + ":" + resultPath)  #Send the results to C#


def core(DataString):
    """
    :param DataString: a string formated in json containing a dictionnary of data coming from C#
    :return: print key:output
    """
    # print("input in python is\n",DataString)
    result = r.SharedSolverResult() #initialize empty results
    data = json.loads(DataString, object_hook = d.ToSharedDataObject)  #Data are stored in SharedData object

    if isinstance(data, d.SharedData):#check that data is a SharedData object !
        Struct = StructureObj() #initial empty structure 
        #Struct.ModuleDynamics(data) #do some calculations
        result.PopulateWith_Dynamics(Struct) #register the results
        # print("I finished calculation")

    output_dct = json.dumps(result, cls=r.SharedSolverResultEncoder, ensure_ascii=False) #Results are saved as dictionnary JSON. # , indent="\t"
    return output_dct

if __name__ == '__main__': #what happens if called from C#
    main()
