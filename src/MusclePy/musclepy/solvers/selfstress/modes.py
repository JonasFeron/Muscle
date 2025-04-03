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
Localization of self-stress modes in tensegrity and pin-jointed structures.

This module provides methods to transform self-stress modes into "localized" self-stress
modes that activate the minimum number of elements possible, which is particularly 
useful for modular tensegrity structures.

references:
- Feron J., Latteur P., 2023, "Implementation and propagation of prestress forces in 
  pin-jointed and tensegrity structures, Engineering Structures, 289, 116152"
- Sánchez R., Maurin B., Kazi-Aoual M. N., and Motro R., "Selfstress States 
  Identification and Localization in Modular Tensegrity Grids," Int. J. Sp. Struct., 
  vol. 22, no. 4, pp. 215–224, Nov. 2007.
- Sanchez Sandoval L. R., "Contribution à l'étude du dimensionnement optimal 
  des systèmes de tenségrité," Université Montpellier II, 2005, p. 49
"""

from musclepy.femodel.pytruss import PyTruss
import numpy as np


def localize_self_stress_modes(structure : PyTruss, Vs_T : np.ndarray, zero_atol=1e-6) -> np.ndarray:
    """
    Localizes and sorts self-stress modes to minimize the number of elements involved in each mode.
    
    Args:
        structure: Structure object containing element information
        Vs_T: Self-stress modes matrix of shape (s, elements_count). _T stands for Transposed, indicating that one row of Vs_T is one self-stress mode.
        zero_tol: Tolerance for considering values as zero (default: 1e-6)
        
    Returns:
        np.ndarray: Localized and sorted self-stress modes matrix
    """
    # Validate input
    if structure.elements.count == 0:
        raise ValueError("Structure must have elements defined")
    
    # Validate Vs_T shape
    if not isinstance(Vs_T, np.ndarray):  # if Vs_T is a C# array
        Vs_T = np.array(Vs_T, dtype=float, copy=True)
    
    if Vs_T.shape[1] != structure.elements.count:
        raise ValueError("The self-stress modes length must match the number of elements")
    
    # Get dimensions
    s, b = Vs_T.shape
    
    # Get element lengths
    element_lengths = structure.elements.current_length
    L = np.diag(element_lengths)
    Linv = np.diag(1.0 / element_lengths)
    
    # Convert force vectors to force densities, to help with localization
    qs_T = Vs_T @ Linv  # [1/m] - force densities for each self-stress mode
    
    # Apply recursive reduction to localize modes
    qs_T_localized = _recursively_reduce(qs_T, structure.elements.type, zero_atol)
    
    # Sort the localized modes, to have the modes involving the least number of elements first
    qs_T_sorted = _sort_reduced_modes(qs_T_localized, zero_atol)
    
    # Convert back to dimensionless vectors
    Vs_T_sorted = qs_T_sorted @ L
    
    # Normalize each mode
    S_T = np.zeros((s, b))
    for i in range(s):
        S_T[i] = normalize_self_stress_mode(Vs_T_sorted[i], zero_atol)
    
    # Return the localized, sorted and normalized self-stress modes
    return S_T 


def normalize_self_stress_mode(mode, zero_atol=1e-6):
    """
    Normalizes one self-stress mode such that the most compressed element correspond to -1 value.
    If all elements have the same axial force sign, then all elements are supposed to be in tension, with 1 value in the most tensed element.

    Args:
        mode: one self-stress mode vector to normalize
        zero_atol: Tolerance for considering values as zero
        
    Returns:
        np.ndarray: Normalized self-stress mode
    """
    compression_max = mode.min()  # Most negative value (compression)
    tension_max = mode.max()      # Most positive value (tension)
    
    # Determine which is larger in magnitude
    use_compression = -compression_max > tension_max
    max_value = compression_max if use_compression else tension_max
    
    # Normalize so the maximum value is -1 for compression
    normalized_mode = -mode / max_value
          
    # Reverse the sign if all elements are in compression:
    if normalized_mode.max() <= zero_atol:# If mode only has compression (no tension),
        normalized_mode *= -1 # reverse the sign
        
    return normalized_mode


def _recursively_reduce(modes : np.ndarray, elements_type : np.ndarray, zero_atol=1e-6) -> np.ndarray:
    """
    Recursively reduces the self-stress modes to localize them.
    
    This implements the Gauss-Jordan elimination with pivoting to minimize
    the number of elements involved in each self-stress mode.
    
    Args:
        structure: Structure object with element information
        modes: Force density matrix for self-stress modes
        zero_tol: Tolerance for considering values as zero
        
    Returns:
        np.ndarray: Localized (reduced) self-stress modes
    """
    s, b = modes.shape
    if s <= 1:
        return modes
    
    # Validate element types
    if elements_type is None or len(elements_type) != b:
        raise ValueError("Element types must be provided and match the number of elements")
        
    # Count non-zero elements in each mode
    non_zero_mask = ~np.isclose(modes, np.zeros((s, b)), atol=zero_atol)
    elements_per_mode = np.sum(non_zero_mask, axis=1)
    
    # Sort modes by number of elements (descending: most localized (up) to most general (down)) 
    sort_indices = np.argsort(elements_per_mode)
    sorted_modes = modes[sort_indices]
    elements_per_mode_sorted = elements_per_mode[sort_indices]
    
    # Try to reduce modes starting from the most general (with most elements)
    # up to the most localized
    reduction_performed = False
    
    # Loop through modes from most general to most localized
    for j in range(s-1, 0, -1):
        # Try to use each more localized mode to reduce the current mode
        for i in range(0, j):
            # Try each element as a potential pivot
            for k in range(b-1, -1, -1):
                # Skip if either mode has zero at this element
                if (np.isclose(sorted_modes[i][k], 0, atol=zero_atol) or 
                    np.isclose(sorted_modes[j][k], 0, atol=zero_atol)):
                    continue
                
                # Test if reduction would better localize the mode j (reduce the number of elements)
                mode_i = sorted_modes[i].copy()
                mode_j = sorted_modes[j].copy()
                
                # Perform Gauss-Jordan elimination: Lj -> Lj - Li * Lj[k]/Li[k]
                factor = mode_j[k] / mode_i[k]
                mode_j -= mode_i * factor
                
                # Set near-zero values to exactly zero
                mode_j = np.where(np.isclose(mode_j, 0, atol=zero_atol), 0, mode_j)
                
                # Count non-zero elements after reduction
                elements_in_reduced_mode = np.count_nonzero(mode_j)
                
                # Check if reduction is beneficial
                perform_reduction = elements_in_reduced_mode < elements_per_mode_sorted[j]
                
                # If number of elements is unchanged, check if reduction improves element compatibility
                if elements_in_reduced_mode == elements_per_mode_sorted[j]:
                    # Check if more elements conform to their expected behavior
                    # (cables in tension, struts in compression)
                    # Count elements with correct sign before reduction
                    conform_before = np.sum(_is_conform(sorted_modes[j], elements_type))
                        
                    # Count elements with correct sign after reduction
                    conform_after = np.sum(_is_conform(mode_j, elements_type))
                        
                    perform_reduction = conform_after > conform_before
                
                if perform_reduction:
                    # Apply the reduction
                    factor = sorted_modes[j][k] / sorted_modes[i][k]
                    sorted_modes[j] -= sorted_modes[i] * factor
                    sorted_modes[j] = np.where(np.isclose(sorted_modes[j], 0, atol=zero_atol), 0, sorted_modes[j])
                    
                    # Normalize the mode
                    sorted_modes[j] = normalize_self_stress_mode(sorted_modes[j], zero_atol)
                    
                    # Ensure correct sign based on element types
                    conform = np.sum(_is_conform(sorted_modes[j], elements_type))
                    anti_conform = np.sum(_is_conform(-sorted_modes[j], elements_type))
                        
                    if anti_conform > conform:
                        sorted_modes[j] = -sorted_modes[j]
                    
                    reduction_performed = True
                    break
            
            if reduction_performed:
                break
        
        if reduction_performed:
            break
    
    # Recursively continue reduction if changes were made
    if reduction_performed:
        sorted_modes = _recursively_reduce(sorted_modes, elements_type, zero_atol)
    
    return sorted_modes

def _is_conform(tension, type):
    """
    Checks if the axial force in each element is of the correct sign for its type.
    
    Parameters
    ----------
    tension : np.ndarray
        Axial forces in the elements (tension >0, compression <0)
    type : np.ndarray
        Elements' type (1 if elements withstand only tension, -1 if withstand only compression, 0 if withstand both)
    
    Returns
    -------
    np.ndarray
        Boolean array indicating whether the element withstands the sign of the axial force or not
    """
    # assert the shape of tension and type
    assert tension.shape == type.shape, "Tension and type arrays must have the same shape"
    
    # For elements that withstand only tension (type=1), tension should be ≥ 0
    # For elements that withstand only compression (type=-1), tension should be ≤ 0
    # For elements that withstand both (type=0), any tension value is acceptable
    
    # Elements that can only be in tension (cables)
    tension_only_mask = (type == 1) 
    tension_conform = np.logical_or(tension >= 0, ~tension_only_mask) # Is it in tension ? Or does it withstand compression ? 1 YES -> conform
    
    # Elements that can only be in compression (struts)
    compression_only_mask = (type == -1)
    compression_conform = np.logical_or(tension <= 0, ~compression_only_mask) # Is it in compression ? Or does it withstand tension ? 1 YES -> conform
    
    # Elements conform if they satisfy both conditions
    return np.logical_and(tension_conform, compression_conform)

def _sort_reduced_modes(reduced_modes, zero_tol=1e-6):
    """
    Sorts the reduced self-stress modes by their first active element.

    This function groups modes with the same number of active elements and sorts them
    based on the first active element index
    
    Args:
        reduced_modes: Reduced self-stress modes matrix
        zero_tol: Tolerance for considering values as zero
        
    Returns:
        np.ndarray: Sorted self-stress modes
    """
    s, b = reduced_modes.shape
    if s <= 1:
        return reduced_modes
    
    # Count non-zero elements in each mode
    non_zero_mask = ~np.isclose(reduced_modes, np.zeros((s, b)), atol=zero_tol)
    elements_per_mode = np.sum(non_zero_mask, axis=1)
    
    # Find groups of modes with the same number of elements
    unique_counts = np.unique(elements_per_mode)
    
    # Sort each group separately
    sorted_modes = np.zeros_like(reduced_modes)
    current_index = 0
    
    for count in unique_counts:
        # Get indices of modes with this count
        group_indices = np.where(elements_per_mode == count)[0]
        group_size = len(group_indices)
        
        # Extract the group of modes
        group_modes = reduced_modes[group_indices]
        
        # Sort this group by the index of their first non-zero element
        sorted_group = _sort_mode_group(group_modes, zero_tol)
        
        # Place sorted group in the result array
        sorted_modes[current_index:current_index+group_size] = sorted_group
        current_index += group_size
    
    return sorted_modes


def _sort_mode_group(group_modes, zero_tol=1e-6):
    """
    Sorts a group of self-stress modes by the index of their first non-zero element.
    
    Args:
        group_modes: a Group of self-stress modes with the same number of elements
        zero_tol: Tolerance for considering values as zero
        
    Returns:
        np.ndarray: Sorted group of modes
    """
    sub_s, b = group_modes.shape
    if sub_s <= 1:
        return group_modes
    
    # Find the index of the first non-zero element in each mode
    first_indices = np.zeros(sub_s, dtype=int)
    
    for i in range(sub_s):
        mode = group_modes[i]
        non_zero_indices = np.where(~np.isclose(mode, 0, atol=zero_tol))[0]
        if len(non_zero_indices) > 0:
            first_indices[i] = non_zero_indices[0]
        else:
            first_indices[i] = b  # Place modes with all zeros at the end
    
    # Sort by first non-zero index
    sort_indices = np.argsort(first_indices)
    return group_modes[sort_indices]