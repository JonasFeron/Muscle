# MusclePy

## Overview
MusclePy is a Python package for structural analysis that focuses on the design, analysis, and optimization of tensegrity, tension-based, and truss-like structures.

## Features
- **Finite Element Modeling**: Create and manipulate structural models with `PyNodes`, `PyElements`, and `PyTruss`
- **Singular Value Decomposition (SVD)**: Analyze equilibrium matrices to identify mechanisms and self-stress modes
- **Self-stress Modes**: Localize and sort self-stress modes in tensegrity structures
- **Displacement Methods**: Solve structural problems using linear and nonlinear displacement methods
- **Dynamic Relaxation**: Form-finding and analysis using dynamic relaxation techniques

## Installation
```bash
pip install musclepy
```

## Quick Start
```python
import musclepy as mp

# Create a simple structure
nodes = mp.PyNodes()
elements = mp.PyElements(nodes)
truss = mp.PyTruss(nodes, elements)

# Add nodes and elements
# ...

# Compute SVD
results = mp.main_singular_value_decomposition(truss)

# Localize self-stress modes
localized_modes = mp.localize_self_stress_modes(results.self_stress_modes)
```

## License
Licensed under the Apache License, Version 2.0

## Citation
If you use MusclePy in your research, please cite:
```
Feron J., Payen B., Pacheco De Almeida J., Latteur P. MUSCLE: a new open-source Grasshopper plug-in for the interactive design of tensegrity structures.International Association for Shell and Spatial Structures (IASS) 2024 (Zurich, du 26/08/2024 au 29/08/2024).
```

## Contact
Professor Pierre LATTEUR - pierre.latteur@uclouvain.be - supervisor of the research project.
