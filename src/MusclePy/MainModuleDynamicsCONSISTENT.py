import data as d
import result as r
from StructureObj import StructureObj
import sys
import json


def main(json_data):

    data = json.loads(json_data, object_hook = d.ToSharedDataObject)

    result = core(data)

    json_result = json.dumps(result, cls=r.SharedSolverResult_dynamicsEncoder, ensure_ascii=False) #Results are saved as dictionnary JSON. # , indent="\t"
    return json_result



def core(data):
    result = r.SharedSolverResult_dynamics() #initialize empty results
    if isinstance(data, d.SharedData):#check that data is a SharedData object !
        Struct = StructureObj() #initial empty structure
        Struct.ModuleDynamics_CONSISTENT(data) #do some calculations
        result.PopulateWith_Dynamics(Struct) #register the results
    return result
