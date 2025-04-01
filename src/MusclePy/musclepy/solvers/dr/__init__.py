# Muscle

# Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# List of the contributors to the development of Muscle: see NOTICE file.
# Description and complete License: see NOTICE file.


# Acknowledgements:
# The author wishes to express his sincere appreciation to Professor L. Rhode-Barbarigos (University of Miami) for his substantial guidance in the implementation of the Dynamic Relaxation method in 2021.

"""
musclepy.solvers.dr - Dynamic Relaxation solver

This module implements the Dynamic Relaxation method for structural analysis.

References:
[1] Bel Hadj Ali N., Rhode-Barbarigos L., Smith I.F.C., "Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm", International Journal of Solids and Structures, Volume 48, Issue 5, 2011, Pages 637-647, https://doi.org/10.1016/j.ijsolstr.2010.10.029.
[2] Barnes MR., "Form Finding and Analysis of Tension Structures by Dynamic Relaxation". International Journal of Space Structures. 1999;14(2):89-104. doi:10.1260/0266351991494722
"""

from .main import main_dynamic_relaxation
from .py_config_dr import PyConfigDR
from .py_truss_dr import PyTrussDR
from .py_nodes_dr import PyNodesDR
from .py_elements_dr import PyElementsDR

__all__ = ['main_dynamic_relaxation', 'PyElementsDR', 'PyTrussDR', 'PyNodesDR', 'PyConfigDR']
