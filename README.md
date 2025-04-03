# Muscle

## Overview
Muscle is an open-source Grasshopper plugin for the interactive design, analysis, and optimization of tensegrity, tension-based, and truss-like structures. It combines the power of Python's numerical computing capabilities with Grasshopper's parametric design environment to provide a comprehensive toolkit for structural engineers, architects, and researchers. 

## Key Features
- **Finite Element Modeling**: Create and manipulate truss-like finite element models from within Grasshopper
- **Singular Value Decomposition (SVD)**: Analyze equilibrium matrices to identify mechanisms and self-stress modes
- **Self-stress Modes**: Localize and sort self-stress modes in tensegrity structures
- **Displacement Methods**: Solve structural problems using linear and nonlinear displacement methods
- **Dynamic Relaxation**: Form-finding, deployment and nonlinear analysis using dynamic relaxation techniques
- **Interactive Design**: Seamless integration with Grasshopper's parametric modeling environment

## Installation Instructions
The installation is an easy 3 step process:
1. Install Anaconda3 
2. Install the python library musclepy
3. Install the Grasshopper plugin Muscle

Some grasshopper components of Muscle launch external python scripts for the structural analysis. The python scripts are contained in the "musclepy" library. Anaconda3 is required to run the python scripts.

### 1. Install Anaconda3
[Download here](https://www.anaconda.com/download)

Anaconda3 is a free and open-source distribution of Python programming languages. It is available for Windows, macOS, and Linux. Follow the recommended installation. 

### 2. Install the python library "musclepy"
1. Once Anaconda3 is installed, open the Anaconda Prompt executable
2. Run the following 'one-line' command:

```bash
conda create -n muscle python=3.12.7 -y && conda activate muscle && pip install musclepy
```

This single command will create a new Python environment named "muscle" and install the "musclepy" library along with its dependencies, "numpy" and "scipy".

Note: The structural analysis functionality in "musclepy" is also available as a standalone [Python package](https://pypi.org/project/musclepy/), independent of the Grasshopper plugin.

### 3. Install the plugin "Muscle" for Grasshopper (Rhino 7)
1. Open Rhino 7 (not Grasshopper) 
2. Run the command `_PackageManager`
3. Search for "Muscle" in the package manager and Install.
4. Restart Rhino
5. The Muscle components will be available in Grasshopper under the "Muscle" tab

Congratulations! You have successfully installed the Muscle plugin.

## Getting Started
1. On the Grasshopper canvas, drop the StartPython.NET component from the "0.Initialize Python" tab.
2. Connect a toggle to the first entry of the StartPython.NET component and set the toggle to True. 
3. Explore the examples provided in the `examples` folder for guidance

## Examples
The repository includes several example files demonstrating different capabilities:
- Various geometric configurations
- Linear truss analysis
- Tensegrity simplex structure, along with experimental validation

## Architecture
MUSCLE is built with a dual-language approach:
- **C#**: Used for Grasshopper components and user interface
- **Python**: Implements the finite element methods and structural analysis
- **Python.NET**: Bridges the two languages for seamless integration

The software follows a clean, modular architecture that separates concerns:
- **Muscle**: User interface layer (Grasshopper components)
- **MuscleApp**: Application layer (ViewModel)
- **MuscleCore**: Core layer (Model in C#)
- **MusclePy**: Computational core (Model in Python)

## License
Licensed under the Apache License, Version 2.0

## Copyright
Copyright (C) 2015-2025 Université catholique de Louvain (UCLouvain)

## Citation
If you use MUSCLE in your research, please cite:
```
Feron J., Payen B., Pacheco De Almeida J., Latteur P. MUSCLE: a new open-source Grasshopper plug-in for the interactive design of tensegrity structures. International Association for Shell and Spatial Structures (IASS) 2024 (Zurich, du 26/08/2024 au 29/08/2024).
```

## Acknowledgments
The author is indebted to 
- Prof. Pierre LATTEUR (Supervisor UCLouvain), 
- BESIX (Dr. Ir. Thomas VANDENBERGH, Ir. Pierre MENGEOT), 
- Brussels Capital Region - Innoviris,
- Prof. Landolf RHODE-BARBARIGOS (University of Miami), 
- Prof. João PACHECO DE ALMEIDA and Prof. Jean-Francois REMACLE (UCLouvain),
- Prof. Vincent DENOËL (ULiège)
for their guidance.

## Funding
The development of Muscle was funded by Brussels Capital Region – Innoviris (Grant number 2020-AppliedPhD-107) from 2019 to 2023.

## Contact
Professor Pierre LATTEUR - pierre.latteur@uclouvain.be - supervisor of the research project.

## Contributing
We welcome contributions from the community. Please see the developer documentation in `src/README.md` for more information on the software architecture and how to contribute.
