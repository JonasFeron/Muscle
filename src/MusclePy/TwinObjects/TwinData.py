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

# this file was imported from https://github.com/JonasFeron/PythonConnectedGrasshopperTemplate and is used without modification.
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

import numpy as np


class TwinData():
    def __init__(self, TypeName,
                 AList,
                 rowNumber,
                 colNumber): #the Names of the __init__(arguments) must be identical to the Names of the TwinData properties in C#
        """
        Initialize all the properties of a TwinData Object.
        A TwinData Object is an object that contains the same data in C# than in Python in order to communicate between the two languages via a file.txt encrypted in json format.
        """
        self.TypeName = TypeName
        self.AList = np.array(AList, dtype=int)  #input arguments from C# are lists which are converted in numpy.array
        self.rowNumber = rowNumber
        self.colNumber = colNumber

def ToTwinDataObject(dct):
    """
    Function that takes in a dictionary and returns a TwinData object associated to the dict.
    """
    if 'TwinData' in dct.values(): # if TypeName == 'TwinData':
        return TwinData(**dct) #call the constructor of TwinData with all the values of the dictionnary.
    return dct

