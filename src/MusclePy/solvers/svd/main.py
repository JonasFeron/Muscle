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

from MusclePy.solvers.svd.py_results_svd import PyResultsSVD
from MusclePy.femodel.pytruss import PyTruss
from MusclePy.utils.matrix_calculations import compute_equilibrium_matrix
import numpy as np


def main_singular_value_decomposition(structure: PyTruss, zero_rtol: float = 1e-3) -> PyResultsSVD:
    """
    Compute the Singular Value Decomposition of the Equilibrium Matrix of the structure
    
    Args:
        structure: PyTruss instance to analyze
        zero_rtol: Tolerance for considering singular values as zero, relative to the highest singular value
            
    Returns:
        PyResultsSVD: Object containing the SVD results
    """
    # 1) Validate input structure
    assert isinstance(structure, PyTruss), "Input structure must be an instance of PyTruss"
       
    # 2) Retrieve structure properties
    n = structure.nodes.count
    b = structure.elements.count
    dof = structure.nodes.dof.reshape((-1,)) #true if free DOF, false if fixed DOF (Degree of Freedom)
    n_dof = dof.sum() # 3 n - fixations_count
    
    # 3) Compute equilibrium matrix based on current nodes coordinates
    A_3n = compute_equilibrium_matrix(structure.elements.connectivity, structure.nodes.coordinates) # shape (3*n, b)
    A = A_3n[dof, :] # shape (3 n - fixations_count, b)
        
    # 4) Validate the equilibrium matrix
    assert A.shape == (n_dof, b), "Please check the equilibrium matrix (A) shape"
    
    # 5) Compute the SVD
    # Note: U contains column eigenvectors (n_dof, n_dof)
    #       Sval contains singular values in decreasing order
    #       V_T contains row eigenvectors (b, b)
    U, Sval, V_T = np.linalg.svd(A)
    
    # 6) Determine rank and degrees of indeterminacy
    Smax = Sval.max() 
    zero = Smax * zero_rtol  # Tolerance for zero singular values
    Sr = Sval[Sval >= zero]  # r Non-zero singular values
    r = Sr.size  # Rank of equilibrium matrix
    m = n_dof - r  # Degree of kinematic indeterminacy (mechanisms)
    s = b - r  # Degree of static indeterminacy (self-stress modes)
        
    # 7) Reformat element space eigenvectors
    V = V_T.T
    Vr = V[:,:r]        # r extensional modes 
    Vs = np.zeros((b, s))   # s self-stress modes 
    if s > 0:
        Vs = V[:,r:]  # the s last remaining columns 
        
    # 8) Reformat node space eigenvectors from (n_dof, r+m) to (3n, r+m) : the fixed DOF are filled with 0 at the supports. 
    U_3n = np.zeros((3*n, r+m))
    U_3n[dof, :] = U

    Ur_3n = U_3n[:, :r]  # r extensional modes
    Um_3n = np.zeros((3*n, m))  # m inextensional modes
    if m > 0:
        Um_3n= U_3n[:, r:]  # # the m last remaining columns 

    # 9) Create and return PyResultsSVD object
    return PyResultsSVD(
            r=r,
            s=s,
            m=m,
            Ur=Ur_3n, 
            Um=Um_3n,  
            Sr=Sr,
            Vr=Vr,
            Vs=Vs   
        )
