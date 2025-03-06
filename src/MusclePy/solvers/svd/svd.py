from MusclePy.femodel.svd_results import SVDresults
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.solvers.svd.structure_svd import Structure_SVD
import numpy as np


class SingularValueDecomposition:
    """Core implementation of the Singular Value Decomposition."""

    @staticmethod
    def core(structure: FEM_Structure, zero_tol: float = 1e-3) -> SVDresults:
        """
        Compute the Singular Value Decomposition of the Equilibrium Matrix of the structure
        
        Args:
            structure: FEM_Structure instance to analyze
            zero_tol: Tolerance for considering singular values as zero
            
        Returns:
            SVDresults: Object containing the SVD results
        """
        # 1) Validate input structure
        assert isinstance(structure, FEM_Structure), "Input structure must be an instance of FEM_Structure"
        
        # 2) Convert FEM_Structure to Structure_SVD if needed
        if not isinstance(structure, Structure_SVD):
            structure = Structure_SVD(structure.nodes, structure.elements)
        
        # 3) Retrieve structure properties
        n = structure.nodes.count
        b = structure.elements.count
        dof = structure.nodes.dof.reshape((-1,)) #true if free DOF, false if fixed DOF (Degree of Freedom)
        n_dof = dof.sum() # 3 n - fixations_count
        
        # 4) Get equilibrium matrix for free DOFs
        A = structure.A
        
        # 5) Validate the equilibrium matrix
        assert A.shape == (n_dof, b), "Please check the equilibrium matrix (A) shape"
        assert np.abs(A).sum() != 0, "Please check that the equilibrium matrix (A) has been computed"
        
        # 6) Calculate the SVD
        # Note: U contains column eigenvectors (n_dof, n_dof)
        #       Sval contains singular values in decreasing order
        #       V_row contains row eigenvectors (b, b)
        U, Sval, V_row = np.linalg.svd(A)
        
        # 7) Determine rank and degrees of indeterminacy
        Smax = Sval.max() 
        tol = Smax * zero_tol  # Tolerance for zero singular values
        Sr = Sval[Sval >= tol]  # r Non-zero singular values
        r = Sr.size  # Rank of equilibrium matrix
        m = n_dof - r  # Degree of kinematic indeterminacy (mechanisms)
        s = b - r  # Degree of static indeterminacy (self-stress modes)
        
        # 8) Reformat element space eigenvectors
        V = V_row.T
        Vr = V[:,:r]        # r extensional modes 
        Vs = np.zeros((b, s))   # s self-stress modes 
        if s > 0:
            Vs = V[:,r:]  # the s last remaining columns 
        
        # 9) Reformat node space eigenvectors from (n_dof, r+m) to (3n, r+m) : there are still r+m column vectors, but the fixed DOF are filled with 0 at the supports. 
        U_3n = np.zeros((3*n, r+m))
        U_3n[dof, :] = U

        Ur_3n = U_3n[:, :r]  # r extensional modes
        Um_3n = np.zeros((3*n, m))  # m inextensional modes
        if m > 0:
            Um_3n= U_3n[:, r:]  # # the m last remaining columns 

       
        # 10) Create and return SVDresults object
        return SVDresults(
            r=r,
            s=s,
            m=m,
            Ur=Ur_3n, 
            Um=Um_3n,  
            Sr=Sr,
            Vr=Vr,
            Vs=Vs   
        )
