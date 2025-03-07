"""
MusclePy.solvers.dr - Dynamic Relaxation solver

This module implements the Dynamic Relaxation method for structural analysis,
following the approach described in:
[1] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm
[2] Barnes, 1999, Form finding and analysis of tension structures by dynamic relaxation
"""

from .dr import DynamicRelaxation
from .dr_config import DRconfig
from .structure_dr import Structure_DR

__all__ = ['DynamicRelaxation', 'DRconfig', 'Structure_DR']
