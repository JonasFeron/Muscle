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

"""
MusclePy is a Python package for structural analysis developed by Université catholique de Louvain (UCLouvain). It focuses on the design, analysis, and optimization of tensegrity, tension-based, and truss-like structures.
"""

# Define version first
__version__ = "0.0.1"

# Import subpackages 
from . import femodel

# Expose key classes at package level
from .femodel.pynodes import PyNodes
from .femodel.pyelements import PyElements
from .femodel.pytruss import PyTruss

# import subpackages solvers
from . import solvers

# Expose solver functions - these imports should be after solvers is imported
from .solvers.test.test_script import main as test_script_main
from .solvers.svd.main import main_singular_value_decomposition
from .solvers.selfstress.modes import localize_self_stress_modes
from .solvers.dm.linear_dm import main_linear_displacement_method
from .solvers.dm.nonlinear_dm import main_nonlinear_displacement_method
from .solvers.dr.main import main_dynamic_relaxation
from .solvers.svd.py_results_svd import PyResultsSVD
from .solvers.dr.py_config_dr import PyConfigDR

__all__ = [
    'femodel',
    'solvers',
    'test_script_main',
    'PyNodes',
    'PyElements',
    'PyTruss',
    'PyResultsSVD',
    'PyConfigDR',
    'main_singular_value_decomposition',
    'localize_self_stress_modes',
    'main_linear_displacement_method',
    'main_nonlinear_displacement_method',
    'main_dynamic_relaxation'
]