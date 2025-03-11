"""
MusclePy.solvers.dr - Dynamic Relaxation solver

This module implements the Dynamic Relaxation method for structural analysis,
following the approach described in:
[1] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm
[2] Barnes, 1999, Form finding and analysis of tension structures by dynamic relaxation
"""

from .main import main_dynamic_relaxation
from .dr_config import DRconfig
from .dr_structure import DR_Structure
from .dr_nodes import DR_Nodes
from .dr_elements import DR_Elements

__all__ = ['main_dynamic_relaxation', 'DRconfig', 'DR_Structure', 'DR_Nodes', 'DR_Elements']
