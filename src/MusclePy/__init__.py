"""
MusclePy - A Python package for structural analysis
"""

from . import femodel
from . import solvers
from .main_linear_dm import main_linear_displacement_method
from .test_script import main as test_script_main

# Expose key classes at package level
from .femodel import FEM_Nodes, FEM_Elements, FEM_Structure

__version__ = "0.1.0"
__all__ = [
    'femodel',
    'solvers',
    'main_linear_displacement_method',
    'test_script_main',
    'FEM_Nodes',
    'FEM_Elements', 
    'FEM_Structure'
]