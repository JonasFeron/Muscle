"""
MusclePy - A Python package for structural analysis
"""

from . import femodel
from . import solvers
from .test_script import main as test_script_main

# Expose key classes at package level
from .femodel.fem_nodes import FEM_Nodes
from .femodel.fem_elements import FEM_Elements
from .femodel.fem_structure import FEM_Structure
from .femodel.prestress_increment import PrestressScenario
from .solvers.svd.svd_results import SVDresults
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
    'FEM_Nodes',
    'FEM_Elements', 
    'FEM_Structure',
    'PrestressScenario',
    'main_singular_value_decomposition',
    'localize_self_stress_modes',
    'SVDresults',
    'main_linear_displacement_method',
    'main_nonlinear_displacement_method',
    'main_dynamic_relaxation',
    'main_dynamic_modal_analysis',
    'DynamicResults'
]