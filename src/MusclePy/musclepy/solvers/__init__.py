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
musclepy.solvers - Collection of structural analysis solvers
"""

# Import submodules first
from . import dm
from . import dr
from . import svd
from . import selfstress
from . import test

# Expose key solver functions
from .svd.main import main_singular_value_decomposition
from .svd.py_results_svd import PyResultsSVD
from .selfstress.modes import localize_self_stress_modes
from .dm.linear_dm import main_linear_displacement_method
from .dm.nonlinear_dm import main_nonlinear_displacement_method
from .dr.main import main_dynamic_relaxation
from .test.test_script import main as test_script_main

# Define __all__ 
__all__ = [
    'dm', 'dr', 'svd', 'selfstress', 'test',
    'main_singular_value_decomposition',
    'PyResultsSVD',
    'localize_self_stress_modes',
    'main_linear_displacement_method',
    'main_nonlinear_displacement_method',
    'main_dynamic_relaxation',
    'test_script_main'
]

