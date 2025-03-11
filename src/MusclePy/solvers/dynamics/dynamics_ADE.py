    def InitializeDynamic(Self,Data):#Initialize all the data for the dynamic computation

        Self.Initial.NodesCoord = Data.NodesCoord
        Self.ElementsType = Data.ElementsType
        Self.ElementsEndNodes = Data.ElementsEndNodes
        Self.ElementsA = Data.ElementsA
        Self.ElementsE = Data.ElementsE
        Self.MaxFreqWanted = Data.MaxFreqWanted
        Self.NodesCount = Data.NodesCoord.reshape(-1, 3).shape[0]
        Self.ElementsCount = Self.ElementsEndNodes.shape[0]
        Self.IsDOFfree = Data.IsDOFfree
        Self.Initial.Tension = Data.TensionInit
        Self.DOFfreeCount = np.sum(np.ones(3 * Self.NodesCount, dtype=int)[Self.IsDOFfree])
        Self.FixationsCount = 3 * Self.NodesCount - Self.DOFfreeCount

        Self.DynMasses = Data.DynamicMass
        Self.MaxFreqWanted = Data.MaxFreqWanted

    def ModuleDynamics(Self,Data): #Data ? DynamicMass,MaxFreqWanted
        #LUMPED MASS MATRIX
        #Used via C# for the dynamic computation
        """
        Test the function before using the module that compute the natural frequency for a certain prestress and mass on the given geometry
        Input:
            :param NodesCoord : coordinates of the nodes
            :param prestrainLevel : Applied prestress in [kN] - constant
            :param Masses : Masses at each node [Kg] - [ integer ] (LUMPED MODEL)
            :param Applied Prestress

            :return omega : array containing the natural frequencies of the structure
            :return PHI : vector containing the modes for each natural frequency
            #The returns are sorted from small to large frequencies

        """


        Self.InitializeDynamic(Data)

        Self.C = Self.ConnectivityMatrix( Self.NodesCount, Self.ElementsCount, Self.ElementsEndNodes)
        Self.DOFfreeCount = 3 * Self.NodesCount - Self.FixationsCount

        #We consider here the initial shape of the structure : underformed due to prestress or external loads
    
        #Self.Initial.NodesCoord
        (l, ElementsCos) = Self.Initial.ElementsLengthsAndCos(Self, Self.Initial.NodesCoord) # Compute the length and the cosinus director in the initial geomety of the struture
        #(A, AFree, AFixed) = Self.Initial.EquilibriumMatrix(Self, ElementsCos) # Compute the equilibrium matrix in the initial state [All dof, free dof, fixed dof]
        
        #Retrive the Young Modulus and areas in function of the caracter of the internal forces of the members : tension or compression
        Self.Initial.ElementsE = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsE)
        Self.Initial.ElementsA = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsA)
        
        
        #The tension in the structure contain already the influence of the load and the pretension due to Lfree < L


        # Compute the K_geo - the rigidity matrix due to the Prestress
            #1 - Compute the force densities for each member  - Q [ #member] = F/l [N/m]
            #The forces can come from the pretension (Lfree) or the applied load

        Q = Self.Initial.ForceDensities(Self.Initial.Tension , l) #take the initial tension

            # 2 - Obtain a list containing the local rigidity matrix for each member
        kgLocList = Self.Initial.GeometricLocalStiffnessList(Self, Q)
            #3 - Construct the global stiffness matrix of the structure
        Kgeo = Self.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Self.IsDOFfree].T[Self.IsDOFfree].T # Obtain the Final matrix with only the free DOF

        # Compute the K_mat - the rigidity matrix linked to the material rigidity
        # The material rigidity is only axial
        # Consider that each node is hinged

            # 1 - obtain the list of the local K_mat of each member
        kmatLocList = Self.Initial.MaterialLocalStiffnessList(Self, l, ElementsCos, Self.Initial.ElementsA,
                                                                Self.Initial.ElementsE)
            # 2 - Obtain the global stiffness matrix of the structure
        Kmat = Self.LocalToGlobalStiffnessMatrix(kmatLocList)
        KmatFree = Kmat[Self.IsDOFfree].T[Self.IsDOFfree].T

        KFree = KmatFree + KgeoFree # [N/m]

        # Used units
        # K_geo = [N/m]
        # K_mat = [N/m]

        # Mass matrix used for the dynamics part
        # Need to use Masses from "DynMasses" variable
        # "DynMasses" [ # of nodes]

        ##MassesDirection = np.repeat(Data.DynMasses,3) # Vector [3* # Nodes] containing in each direction the dynamic mass
        # MassesDOF is made the most general : 3 dimensions
        # The masses for each DOF is obtained by decreasing the size of the MassesDiag size
        ##MassesDiag = np.diag(MassesDirection) # Contain all the directions


        Self.DynMasses = np.abs(Self.DynMasses)

        if len(Self.DynMasses) != Self.NodesCount: #The length need to be equal to the number of nodes
            Self.DynMasses = np.ones(Self.NodesCount)

        
        if np.any(Self.DynMasses,0) == False: #No mass equal to zero in the vector
            Self.DynMasses = np.ones(Self.NodesCount)

        MassesDiag = np.diag(np.repeat(Self.DynMasses,3))
        MassesDiagFree = MassesDiag[Self.IsDOFfree].T[Self.IsDOFfree].T #Retrieve the masses linked to free direction, DOF


        # Compute the eigen values of the problem - natural frequencies
        # Made via the characteristic equation : det ( K - \omega_i M ) = 0

        w2, PHI = np.linalg.eig(np.linalg.inv(MassesDiagFree)@KFree) #squared natural frequencies and the modes
        w = np.sqrt(w2)

        # Sort the frequencies and the modes from small to high frequencies
        # Convention
        idx = w.argsort()[::1]
        w = w[idx]
        PHI = PHI[:, idx]
        
        #Insert the results
        Self.freq = w/(2*np.pi) 
        Self.mode = PHI


        #TotMode : insert all the displacement of the mode considering that for the Non DOF that the displacement is zero
        Self.TotMode = np.zeros((len(Self.IsDOFfree),Self.DOFfreeCount))
        Self.TotMode[Self.IsDOFfree] = Self.mode
        
        #Return a part of the computed elements in function of the value of MaxFreqWanted
        if Self.MaxFreqWanted != 0:
            if Self.MaxFreqWanted < Self.DOFfreeCount:
                Self.freq = Self.freq[:Self.MaxFreqWanted]
                Self.mode = Self.mode[:,:Self.MaxFreqWanted]
                Self.TotMode = Self.TotMode[:,:Self.MaxFreqWanted]

            else:
                Self.MaxFreqWanted = Self.DOFfreeCount
        else:
            Self.MaxFreqWanted = Self.DOFfreeCount
        


    def InitializeDynamic_CONSISTENT(Self,Data):#Initialize all the data for the dynamic computation

        Self.Initial.NodesCoord = Data.NodesCoord
        Self.ElementsType = Data.ElementsType
        Self.ElementsEndNodes = Data.ElementsEndNodes
        Self.ElementsA = Data.ElementsA
        Self.ElementsE = Data.ElementsE
        Self.MaxFreqWanted = Data.MaxFreqWanted
        Self.NodesCount = Data.NodesCoord.reshape(-1, 3).shape[0]
        Self.ElementsCount = Self.ElementsEndNodes.shape[0]
        Self.IsDOFfree = Data.IsDOFfree
        Self.Initial.Tension = Data.TensionInit
        Self.DOFfreeCount = np.sum(np.ones(3 * Self.NodesCount, dtype=int)[Self.IsDOFfree])
        Self.FixationsCount = 3 * Self.NodesCount - Self.DOFfreeCount

        Self.DynMasses = Data.DynamicMass
        Self.MassElement = Data.MassElement
        Self.MaxFreqWanted = Data.MaxFreqWanted


    def ModuleDynamics_CONSISTENT(Self,Data): #Data ? DynamicMass,MaxFreqWanted
        #CONSISTENT MASS MATRIX
        #Used via C# for the dynamic computation
        """
        Test the function before using the module that compute the natural frequency for a certain prestress and mass on the given geometry
        Input:
            :param NodesCoord : coordinates of the nodes
            :param prestrainLevel : Applied prestress in [kN] - constant
            :param Masses : Masses at each node [Kg] - [ integer ] (CONSISTENT MODEL)
            :param Applied Prestress

            :return omega : array containing the natural frequencies of the structure
            :return PHI : vector containing the modes for each natural frequency
            #The returns are sorted from small to large frequencies

        """


        Self.InitializeDynamic_CONSISTENT(Data)

        Self.C = Self.ConnectivityMatrix( Self.NodesCount, Self.ElementsCount, Self.ElementsEndNodes)
        Self.DOFfreeCount = 3 * Self.NodesCount - Self.FixationsCount

        #We consider here the initial shape of the structure : underformed due to prestress or external loads
    
        #Self.Initial.NodesCoord
        (l, ElementsCos) = Self.Initial.ElementsLengthsAndCos(Self, Self.Initial.NodesCoord) # Compute the length and the cosinus director in the initial geomety of the struture
        #(A, AFree, AFixed) = Self.Initial.EquilibriumMatrix(Self, ElementsCos) # Compute the equilibrium matrix in the initial state [All dof, free dof, fixed dof]
        
        #Retrive the Young Modulus and areas in function of the caracter of the internal forces of the members : tension or compression
        Self.Initial.ElementsE = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsE)
        Self.Initial.ElementsA = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsA)
        
        
        #The tension in the structure contain already the influence of the load and the pretension due to Lfree < L


        # Compute the K_geo - the rigidity matrix due to the Prestress
            #1 - Compute the force densities for each member  - Q [ #member] = F/l [N/m]
            #The forces can come from the pretension (Lfree) or the applied load

        Q = Self.Initial.ForceDensities(Self.Initial.Tension , l) #take the initial tension

            # 2 - Obtain a list containing the local rigidity matrix for each member
        kgLocList = Self.Initial.GeometricLocalStiffnessList(Self, Q)
            #3 - Construct the global stiffness matrix of the structure
        Kgeo = Self.LocalToGlobalStiffnessMatrix(kgLocList)
        KgeoFree = Kgeo[Self.IsDOFfree].T[Self.IsDOFfree].T # Obtain the Final matrix with only the free DOF

        # Compute the K_mat - the rigidity matrix linked to the material rigidity
        # The material rigidity is only axial
        # Consider that each node is hinged

            # 1 - obtain the list of the local K_mat of each member
        kmatLocList = Self.Initial.MaterialLocalStiffnessList(Self, l, ElementsCos, Self.Initial.ElementsA,
                                                                Self.Initial.ElementsE)
            # 2 - Obtain the global stiffness matrix of the structure
        Kmat = Self.LocalToGlobalStiffnessMatrix(kmatLocList)
        KmatFree = Kmat[Self.IsDOFfree].T[Self.IsDOFfree].T

        KFree = KmatFree + KgeoFree  # [N/m]

        # Used units
        # K_geo = [N/m]
        # K_mat = [N/m]

        # Mass matrix used for the dynamics part
        # Need to use Masses from "DynMasses" variable
        # "DynMasses" [ # of nodes]

        ##MassesDirection = np.repeat(Data.DynMasses,3) # Vector [3* # Nodes] containing in each direction the dynamic mass
        # MassesDOF is made the most general : 3 dimensions
        # The masses for each DOF is obtained by decreasing the size of the MassesDiag size
        ##MassesDiag = np.diag(MassesDirection) # Contain all the directions


        Self.DynMasses = np.abs(Self.DynMasses)

        if len(Self.DynMasses) != Self.NodesCount: #The length need to be equal to the number of nodes
            Self.DynMasses = np.ones(Self.NodesCount)

        
        if np.any(Self.DynMasses,0) == False: #No mass equal to zero in the vector
            Self.DynMasses = np.ones(Self.NodesCount)

        MassesDiagNodale = np.diag(np.repeat(Self.DynMasses,3))

        MassesElementMatrix = np.zeros((Self.NodesCount*3,Self.NodesCount*3))

        if len(Self.MassElement) == Self.ElementsCount:

            for i in range(Self.ElementsCount):
                MassToAdd = Self.MassElement[i]
                Node1 = Self.ElementsEndNodes[i,0]
                Node2 = Self.ElementsEndNodes[i,1]
                index = np.array([3 * Node1, 3 * Node1 + 1, 3 * Node1 + 2,
                              3 * Node2, 3 * Node2 + 1, 3 * Node2 + 2]).astype(int)
                indexBis = np.array([3 * Node2, 3 * Node2 + 1, 3 * Node2 + 2,
                              3 * Node1, 3 * Node1 + 1, 3 * Node1 + 2]).astype(int)
                for j in range(6):
                    MassesElementMatrix[index[j],index[j]] += 1/3*MassToAdd
                    MassesElementMatrix[index[j],indexBis[j]] += 1/6*MassToAdd

        
        MassesDiag = MassesDiagNodale + MassesElementMatrix #The matrix is not symmetric

        MassesDiagFree = MassesDiag[Self.IsDOFfree].T[Self.IsDOFfree].T #Retrieve the masses linked to free direction, DOF


        # Compute the eigen values of the problem - natural frequencies
        # Made via the characteristic equation : det ( K - \omega_i M ) = 0

        w2, PHI = np.linalg.eig(np.linalg.inv(MassesDiagFree)@KFree) #squared natural frequencies and the modes
        w = np.sqrt(w2)

        # Sort the frequencies and the modes from small to high frequencies
        # Convention
        idx = w.argsort()[::1]
        w = w[idx]
        PHI = PHI[:, idx]
        
        #Insert the results
        Self.freq = w/(2*np.pi) 
        Self.mode = PHI


        #TotMode : insert all the displacement of the mode considering that for the Non DOF that the displacement is zero
        Self.TotMode = np.zeros((len(Self.IsDOFfree),Self.DOFfreeCount))
        Self.TotMode[Self.IsDOFfree] = Self.mode
        
        #Return a part of the computed elements in function of the value of MaxFreqWanted
        if Self.MaxFreqWanted != 0:
            if Self.MaxFreqWanted < Self.DOFfreeCount:
                Self.freq = Self.freq[:Self.MaxFreqWanted]
                Self.mode = Self.mode[:,:Self.MaxFreqWanted]
                Self.TotMode = Self.TotMode[:,:Self.MaxFreqWanted]

            else:
                Self.MaxFreqWanted = Self.DOFfreeCount
        else:
            Self.MaxFreqWanted = Self.DOFfreeCount


