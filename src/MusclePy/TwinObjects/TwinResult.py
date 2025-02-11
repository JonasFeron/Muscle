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

import json
import numpy as np

class TwinResult():
    def __init__(self):
        """
        initialise empty TwinResult
        """
        self.TypeName = "TwinResult"
        self.Matrix = []

    def populate_with(self, array):
        if isinstance(array, np.ndarray):
            self.Matrix = array.tolist()



class TwinResultEncoder(json.JSONEncoder):
    """
    The TwinResultEncoder class is used to record all the properties of a TwinResult object in a dictionary and send them to C#.
    """
    def default(self, obj):
        if isinstance(obj, TwinResult):
            return obj.__dict__ # obj.__dct__ = {'property': value, ...}
        else : # Let the base class default method raise the TypeError
            return json.JSONEncoder.default(self, obj)
