"""
Example script demonstrating the use of the dynamic modal analysis function.

This script shows how to perform modal analysis on a simple structure
using the compute_modal_analysis function.
"""

import numpy as np
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.utils.matrix_calculations import compute_local_lumped_mass_matrices
from MusclePy.solvers.dynamics.method import main_dynamic_modal_analysis

def run_example():
    """
    Run a simple example of dynamic modal analysis on a 2-cable structure.
    """
    # Create nodes
    coordinates = np.array([
        [0.0, 0.0, 0.0],  # Node 0
        [1.0, 0.0, 0.0],  # Node 1
        [0.5, 0.5, 0.0]   # Node 2
    ])
    
    is_dof_free = np.array([
        [False, False, False],  # Node 0 - fixed
        [False, False, False],  # Node 1 - fixed
        [True, True, True]      # Node 2 - free
    ]).flatten()
    
    nodes = FEM_Nodes(coordinates, is_dof_free)
    
    # Create elements
    end_nodes = np.array([
        [0, 2],  # Element 0
        [1, 2]   # Element 1
    ])
    
    cross_sections = np.array([1e-4, 1e-4])  # m²
    elastic_moduli = np.array([2e11, 2e11])   # N/m² (steel)
    free_lengths = np.array([0.7, 0.7])       # m
    
    elements = FEM_Elements(nodes, end_nodes, cross_sections, elastic_moduli, free_lengths)
    
    # Create structure
    structure = FEM_Structure(nodes, elements)
    
    # Set initial tensions
    structure.elements.tension = np.array([1000.0, 1000.0])  # N
    
    # Create nodal masses (kg)
    nodal_masses = np.array([
        [1.0, 1.0, 1.0],  # Node 0
        [1.0, 1.0, 1.0],  # Node 1
        [2.0, 2.0, 2.0]   # Node 2
    ])
    
    # Create element masses (kg)
    element_masses = np.array([0.5, 0.5])  # kg
    
    # Compute element mass matrices (lumped mass approach)
    element_mass_matrices = compute_local_lumped_mass_matrices(element_masses)
    
    # Perform modal analysis
    results = main_dynamic_modal_analysis(
        structure,
        nodal_masses,
        element_mass_matrices,
        n_modes=3
    )
    
    # Print results
    print("Dynamic Modal Analysis Results:")
    print(f"Number of modes: {results.mode_count}")
    print("\nNatural Frequencies (Hz):")
    for i, freq in enumerate(results.frequencies):
        print(f"Mode {i+1}: {freq:.4f} Hz (Period: {results.periods[i]:.4f} s)")
    
    print("\nMode Shapes (first mode):")
    print(results.get_total_mode(0).reshape(-1, 3))
    
    return results

if __name__ == "__main__":
    run_example()
