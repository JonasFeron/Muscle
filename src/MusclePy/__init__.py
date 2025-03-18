"""
MusclePy - A Python package for structural analysis
"""

from . import femodel
from . import solvers
from .test_script import main as test_script_main

# Expose key classes at package level
from .femodel.pynodes import PyNodes
from .femodel.pyelements import PyElements
from .femodel.pytruss import PyTruss
from .solvers.svd.py_results_svd import PyResultsSVD
from .solvers.dynamic.dynamic_results import DynamicResults

# Expose solver functions
from .solvers.svd.main import main_singular_value_decomposition
from .solvers.svd.self_stress_modes import localize_self_stress_modes
from .solvers.dm.linear_dm import main_linear_displacement_method
from .solvers.dm.nonlinear_dm import main_nonlinear_displacement_method
from .solvers.dr.main import main_dynamic_relaxation
from .solvers.dynamic.main import main_dynamic_modal_analysis

__version__ = "0.1.0"
__all__ = [
    'femodel',
    'solvers',
    'test_script_main',
    'PyNodes',
    'PyElements',
    'PyTruss',
    'main_singular_value_decomposition',
    'localize_self_stress_modes',
    'PyResultsSVD',
    'main_linear_displacement_method',
    'main_nonlinear_displacement_method',
    'main_dynamic_relaxation',
    'main_dynamic_modal_analysis',
    'DynamicResults'
]