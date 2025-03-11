"""
Displacement Method (DM) solvers for structural analysis.

This package contains linear and nonlinear displacement method solvers for structural analysis.
"""

from .linear_dm import main_linear_displacement_method
from .nonlinear_dm import main_nonlinear_displacement_method

__all__ = ['main_linear_displacement_method', 'main_nonlinear_displacement_method']
