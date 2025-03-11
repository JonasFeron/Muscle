import numpy as np
class SVDresults():
    """
    This class stores the results into a SVDresults object of the Singular Value Decomposition of the Equilibrium Matrix of the structure in the current state.
    Ref: S. Pellegrino, 1993, Structural computations with the singular value decomposition of the equilibrium matrix
    """

    def __init__(self, r, s, m, Ur, Um, Sr, Vr, Vs):
        """
        Initialize a SVDresults object that stores the results
        """
        self.r = r #rank of equilibrium matrix
        self.s = s # degree of static indeterminacy = nbr of self-stress modes
        self.m = m # degree of kinematic indeterminacy = nbr of mechanisms

        # r+m left singular vectors of the equilibrium matrix (length= 3*nodes_count, with 0 values where the DOF are fixed by supports)
        self.Ur = Ur # r extensional modes: loads which can be equilibrated in the current structure OR extensional displacements (=which elongate the elements)
        self.Um = Um # m inextensional modes : loads which can't be equilibrated in the current structure OR inextensional displacements (=mechanisms)
        
        self.Sr = Sr # r singular values of the equilibrium matrix

        # right singular vectors of the equilibrium matrix (length= elements_count)
        self.Vr = Vr # r extensional modes: axial forces in equilibrium with extensional loads OR elongations compatible with extensional displacements. 
        self.Vs = Vs # s self-stress modes: axial forces in equilibrium without external loads OR "incompatible" elongations (= elongations that can exist without displacements)

        # note: all vectors are column vectors by default
        # but grasshopper needs their transpose for visualisation purpose

    
    @property
    def Ur_T(self): 
        """
        Returns:
            np.ndarray: Transpose of Ur (3*nodes_count, r) : extensional modes as row vectors
        """
        return self.Ur.T
    
    @property
    def Um_T(self):
        """
        Returns:
            np.ndarray: Transpose of Um (3*nodes_count, m) : inextensional modes as row vectors
        """
        return self.Um.T
    
    @property
    def Vr_T(self):
        """
        Returns:
            np.ndarray: Transpose of Vr (elements_count, r) : extensional modes as row vectors
        """
        return self.Vr.T
    
    @property
    def Vs_T(self):
        """
        Returns:
            np.ndarray: Transpose of Vs (elements_count, s) : self-stress modes as row vectors
        """
        return self.Vs.T