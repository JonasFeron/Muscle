"""
MusclePy.solvers - Collection of structural analysis solvers
"""

from . import dm
from . import dr
from . import svd
from . import dynamic

# Expose key solver functions
from .svd.main import main_singular_value_decomposition
from .svd.py_results_svd import PyResultsSVD
from .svd.self_stress_modes import localize_self_stress_modes
from .dm.linear_dm import main_linear_displacement_method
from .dm.nonlinear_dm import main_nonlinear_displacement_method
from .dr.main import main_dynamic_relaxation
from .dynamic.main import main_dynamic_modal_analysis
from .dynamic.dynamic_results import DynamicResults

__all__ = [
    'dm', 'dr', 'svd', 'dynamic',
    'main_singular_value_decomposition',
    'PyResultsSVD',
    'localize_self_stress_modes',
    'main_linear_displacement_method',
    'main_nonlinear_displacement_method',
    'main_dynamic_relaxation',
    'main_dynamic_modal_analysis',
    'DynamicResults'
]
