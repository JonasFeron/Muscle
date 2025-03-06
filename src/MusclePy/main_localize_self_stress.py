import numpy as np
from MusclePy.solvers.svd.self_stress_modes import SelfStressModes
from MusclePy.femodel.fem_structure import FEM_Structure


def main_localize_self_stress_modes(structure : FEM_Structure, Vs_T : np.ndarray, zero_tol=1e-6) -> np.ndarray:
    """
    Localizes and sorts self-stress modes to minimize the number of elements involved in each mode.
    
    Args:
        structure: Structure object containing element information
        Vs_T: Self-stress modes matrix of shape (s, elements_count). _T stands for Transposed, indicating that one row of Vs_T is one self-stress mode.
        zero_tol: Tolerance for considering values as zero (default: 1e-6)
        
    Returns:
        np.ndarray: Localized and sorted self-stress modes matrix
    """
    S = SelfStressModes.localize(structure, Vs_T, zero_tol)
    
    return S