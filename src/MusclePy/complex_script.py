# PythonNETGrasshopperTemplate

# Copyright <2025> <Jonas Feron>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
# Description and complete License: see NOTICE file.

# this file was imported from https://github.com/JonasFeron/PythonConnectedGrasshopperTemplate and is used quasi without modification.
# ------------------------------------------------------------------------------------------------------------

# Copyright <2021-2025> <Université catholique de Louvain (UCLouvain)>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# List of the contributors to the development of PythonConnectedGrasshopperTemplate: see NOTICE file.
# Description and complete License: see NOTICE file.
# ------------------------------------------------------------------------------------------------------------

import sys
from TwinObjects import TwinData as d
from TwinObjects import TwinResult as r
import json


def main_json_example(json_data):
    """
    This function wraps the process function to:
    1) convert the data from the DataFile.txt into a TwinData object
    2) call process function on TwinData object, and get a TwinResult object
    3) convert the TwinResult object into a JSON string and return it.

    Important note: The function must take a list of strings as input and return a single string as output.
    Args:
        data_lines (list): List of strings where each string is a line from the DataFile.txt. 

    Returns:
        str: a single string containing the result of the function. It will be written to the result file.
    """

    # 1) retrieve data        
    twinData = json.loads(json_data, object_hook = d.ToTwinDataObject)   # the Data read from the data file.txt are stored in TwinData object (identical in python an C#)

    # 2) process data. 
    twinResult = process(twinData)

    # 3) return result. 
    # Results are saved as dictionnary JSON.
    json_result = json.dumps(twinResult, cls=r.TwinResultEncoder, ensure_ascii=False)
    return json_result


def process(twinData):
    """
    Processes the TwinData object and returns a TwinResult object.

    This function takes a TwinData object as input, processes the data by reshaping the array,
    and populates a TwinResult object with the processed data.

    Args:
        twinData (TwinData): The input data to be processed.

    Returns:
        TwinResult: The result of processing the input data.
    """
    twinResult = r.TwinResult() #initialize empty results
    if isinstance(twinData, d.TwinData):#check that data is a TwinData object !
        # Process the data
        # for instance: reshape the array
        array = twinData.AList.reshape(twinData.rowNumber, twinData.colNumber)
        
        # register the results in the TwinResult object
        twinResult.populate_with(array)
        return twinResult
    else:
        return None
    
