# Changelog

All notable changes to musclepy project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-07-21

### Added
- **Dynamic Modal Analysis**: New `musclepy.solvers.dynamic` module for computing natural frequencies and mode shapes
  - `main_dynamic_modal_analysis()` function for modal analysis of structures
  - `PyResultsDynamic` class to store modal analysis results (frequencies, mode shapes, mass matrix)
  - Computation of tangent stiffness matrix including geometric stiffness effects
  - Mass matrix computation with lumped and consistent mass options

### Dependencies
- numpy>=1.26.4
- scipy>=1.13.1
- Python>=3.9

## [1.0.0] - Previous Release

### Added
- Initial release of MusclePy
- Basic finite element modeling capabilities
- SVD analysis for tensegrity structures
- Linear and nonlinear displacement methods
- Dynamic relaxation solver
- Self-stress mode analysis
