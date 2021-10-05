import json
import data as d
import result as r
from StructureObj import StructureObj
import sys


#1) retrieve inputted_data from Grasshopper/C#

#example
#when we run in the terminal:
#python test.py arg1 arg2 arg3
#this lauch test.py
#with the sys.argv = list [test.py, arg1, arg2, arg3]
#

def main():
    key = sys.argv[1] #the Guid
    dataPath = sys.argv[2] #retrieve arg1 sent by C# as an inputted_data
    (key_TxtFile,Data_str) = d.ReadDataFile(dataPath)
    output_str=" "
    if (key  == key_TxtFile):
        try:
            output_str = core(Data_str[0])
        except Exception as e:
            output_str = str(e)
    else:
        output_str = "Keys from command prompt and Data text file did not match"
    resultPath = r.WriteResultFile(dataPath,r.File_LinearSolve_Result,key,output_str)
    print(key + ":" + resultPath)

def core(Data_str):
    """
    :param key: the ID of the c# command executing this script. It allows to connect the command with the results
    :param Data_str: a string formated in json containing a dictionnary of data coming from C#
    :return: print key:output
    """
    # print("input in python is\n",Data_str)
    result = r.SharedSolverResult() #initialize empty results
    data = json.loads(Data_str,object_hook=d.ToSharedDataObject)  #Data are stored in SharedData object

    if isinstance(data, d.SharedData):#check that data is a SharedData object !
        S0 = StructureObj() #initial empty structure
        S0.Main_LinearSolve_Displ_Method(data) #do some calculations
        result.PopulateWith(S0) #register the results
        # print("I finished calculation")

    output_str = json.dumps(result, cls=r.SharedSolverResultEncoder, ensure_ascii=False) #Results are saved as dictionnary JSON. # , indent="\t"
    return output_str

if __name__ == '__main__': #what happens if called from C#
    main()
