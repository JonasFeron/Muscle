
class DRState():
    """
    An extension of the current state object with the data relative to the Dynamic Relaxation in the current state "t"
    """
    def __init__(Cur):
        NodesCount = 0
        #DR.Settings = None #the settings of the DRMethod
        Cur.M = np.zeros((3 * NodesCount,)) # the fictitious mass associated to each DOF
        Cur.V = np.zeros((3 * NodesCount,)) #the velocity of each DOF.  /!\this is the velocity at time t+Dt/2
        Cur.KE = 0 #the total kinetic energy  at time "t". Note that it is calculated based on KE(t) = 0.5 M(t-Dt)*V²(t-Dt/2)

    def Copy(Cur):
        Copy = DRState()
        Copy.M = Cur.M
        Copy.V = Cur.V
        Copy.KE = Cur.KE
        return Copy

    def UpdateResidualAndMass(DRCur, Struct, Cur):
        """
        Update the current DRState by computing the Residual and the mass
        :param Struct:
        :param Cur:
        :return:
        """
        Dt = Struct.DR.Dt
        #Compute Residual
        Cur.ComputeState(Struct,ComputeResidual=True, ComputeStiffness=True)

        # Compute Fictitious Mass
        #Option 1
        # TensionOnly = np.where(Cur.Tension >= 0, Cur.Tension, 0)
        # KgeoInTensionOnly = Cur.GeometricStiffnessMatrix(Struct, TensionOnly, Cur.ElementsL)
        # TempM = DRCur.FictitiousMasses(Struct, Dt, Cur.Kmat, KgeoInTensionOnly)
        # Option 2 reach an equilibrium much (10%) faster !
        TempM = DRCur.FictitiousMasses(Struct, Dt, Cur.Kmat, Cur.Kgeo)
        DRCur.M = DRCur.FictitiousMassesWithSupports(Struct, TempM, Struct.IsDOFfree)  #take the support conditions into account in the mass

    def FictitiousMasses(Cur, Struct, Dt, MaterialStiffnessMatrix, GeometricStiffnessMatrix):
        """
        Compute the fictitious masses for the dynamic relaxation algorithm
        :param Struct: The Structure object in the current state
        :param Dt: [s] - scalar - The time step
        :param MaterialStiffnessMatrix: [N/m] - shape (3*NodesCount,3*NodesCount) - The global material stiffness matrix
        :param GeometricStiffnessMatrix: [N/m] - shape (3*NodesCount,3*NodesCount) - The global geometric stiffness matrix
        :return: M : [kg] - shape (3*NodesCount,) - The fictitious masses for the dynamic relaxation algorithm
        """
        # ref
        # [1] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm

        Kmat = MaterialStiffnessMatrix
        Kgeo = GeometricStiffnessMatrix
        NodesCount = Struct.NodesCount

        assert Kmat.shape == (3 * NodesCount, 3 * NodesCount), "Please check the shape of the global material stiffness matrix Kmat"
        assert Kgeo.shape == (3 * NodesCount, 3 * NodesCount), "Please check the shape of the global geometric stiffness matrix Kgeo"

        # 1) Find the total material stiffness associated to each DOF.
        TotalKmat = np.diag(Kmat)   # shape (3NodesCount, )
        # Each entry i of TotalKmat correspond to the total material stiffness of DOF i
        # (i.e. the resisting forces of the DOF i when the DOF i is moved by a unit displacement).
        # The diagonal of Kmat already considers the sum of the material stiffness for each element.

        # 2) Similarly, Find the total geometric stiffness associated to each DOF.
        TotalForceDensities = np.diag(Kgeo)  # shape (3NodesCount,) - each entry correspond to the sum of T/L for each element connected to the node
        # Only the diagonal of Kgeo is of interest because the sum of each row = 0.
        # ref: Zhang, Ohsaki, 2015, Tensegrity structures: Form, Stability, and Symmetry, p46 equation (2.109) and p109 equation (4.55)

        TotalK = TotalKmat + TotalForceDensities  # equation (20) of ref [1].
        # The differences compared to eq(20) are :
        # - The material stiffness of an element can be = 0 if the cables slack
        # - Tcur/Lcur are not multiplied with the cos².
        # - Tcur is set to 0 only for slack cables, not for compression members. Correction: Tcur is considered as 0 also for compression member

        M = 2 * Dt**2 * TotalK  # equation (19) of ref [1].
        return M

    def FictitiousMassesWithSupports(Cur, Struct, Mass, IsDOFfree):
        AmplMass = Struct.DR.AmplMass
        MinMass = Struct.DR.MinMass
        HugeMass = Struct.DR.HugeMass
        NodesCount = Struct.NodesCount
        assert Mass.shape == (3 * NodesCount,), "Please check the size of Fictitious Mass"
        assert IsDOFfree.shape == (3 * NodesCount,), "Please check the size of the Support Conditions"

        AmplifiedMass = Mass * AmplMass + MinMass
        FinalMass = np.where(IsDOFfree, AmplifiedMass, HugeMass)  # Apply a huge mass where the DOF are fixed (False). Keep the calculated mass otherwise
        return FinalMass


    def Velocities(Cur, Struct, Dt, Residual, Mass):
        """
        Compute the velocities V = Dt*R/M for each DOF
        :param Struct:
        :param Dt: [s] - scalar - the time step
        :param Residual: [N] - shape (3 * NodesCount,) - the unbalanced loads that generate an acceleration
        :param Mass: [kg] - shape (3 * NodesCount,) - the fictitious mass
        :return: V: [m/s] - shape (3 * NodesCount,) - the velocities of each Degree of freedom
        """
        IsDOFfree = Struct.IsDOFfree
        NodesCount = Struct.NodesCount

        assert Residual.shape == (3 * NodesCount,), "Please check Residual and Mass shapes"
        assert Residual.shape == (3 * NodesCount,), "Please check Residual and Mass shapes"
        assert Dt >0, "Please ensure that the DR time step is larger than 0"

        index0 = np.where(np.logical_or(~IsDOFfree,Mass<=0)) # where the DOF are fixed or where the Mass are smaller than or equal to 0.
        TempMass = Mass.copy() # this is needed to avoid modifying the Mass in the next instruction
        TempMass[index0] = 1 # set the mass to 1 to avoid dividing by zero
        V = Dt * Residual/TempMass
        V[index0] = 0 #the velocities are set to 0 where the masses are zero or where the DOF are fixed.
        return V

    def KineticEnergy(Cur, Struct, Mass, Velocity):
        """

        :param Struct: The StructureObj in the current state
        :param Mass: [kg] - shape (3*NodesCount,) - The fictitious mass with huge mass at the supports
        :param Velocity: [m/s] - shape (3*NodesCount,) - the velocities of each Degree of freedom
        :return: KE: [Nm] - scalar - the sum of the total Kinetic Energy in the current state
        """
        IsDOFfree = Struct.IsDOFfree
        NodesCount = Struct.NodesCount

        assert Mass.shape == (3 * NodesCount,), "Please check the Mass shape"
        assert Velocity.shape == (3 * NodesCount,), "Please check the velocity shape"

        KEVector = Mass * Velocity * Velocity
        KE = 0.5 * np.sum(KEVector[IsDOFfree]) # Sum the Kinetic Energy only where there is no support
        return KE



class DRMethod():
    def __init__(DR):
        """
        An object which contains everything needed to perform the dynamic relaxation method on the structure
        """

        DR.AmplMass = 1 #[/] - scalar - the amplification factor of the mass in every DOF in case we run into convergence issue
        DR.MinMass = 0.005 #[kg] - scalar - the min mass applied on every DOF
        DR.HugeMass = 1e15  #[kg] - scalar - huge mass to fix the supports

        DR.Dt = 0.01 #[s] - scalar - the time step of the time incremental method
        DR.nTimeStep = 0  # [/] - scalar - the number of time step such that t = nTimeStep * Dt
        DR.MaxTimeStep = 10000 #[/] - scalar - The maximum number of time increment before the method fails.
        DR.nKEReset = 0 #[/] - scalar - The number of time the Kinetic energy has been reset to 0 at the peaks during the method.
        DR.MaxKeReset = 1000 #[/] - scalar - The maximum number of reset of the Kinetic energy at the peaks before the method fails

    def InitialData(DR,Dt=0.01,AmplMass=1,MinMass=0.005,MaxTimeStep = 10000,MaxKeReset=1000):

        if Dt > 0:
            DR.Dt = Dt
        else:
            DR.Dt = 0.01

        if AmplMass > 0:
            DR.AmplMass = AmplMass
        else:
            DR.AmplMass = 1

        if MinMass > 0:
            DR.MinMass = MinMass
        else:
            DR.MinMass = 0.005

        if MaxTimeStep > 0:
            DR.MaxTimeStep = MaxTimeStep
        else:
            DR.MaxTimeStep = 10000

        if MaxKeReset > 0:
            DR.MaxKeReset = MaxKeReset
        else:
            DR.MaxKeReset = 1000

    def Core(DR,Struct):
        """
        Perform the Dynamic Relaxation Method on the Start State of the Structure.
        This method assumes that the StructureObject has already been initialized with InitialData method
        :return: The final State of the structure in Equilibrium
        """
        #ref:
        # [1] Bel Adj Ali et al, 2011, Analysis of clustered tensegrity structures using a modified dynamic relaxation algorithm
        # [2] Barnes, 1999, Form finding and analysis of tension structures by dynamic relaxation

        # 0) Check inputs
        NodesCount = Struct.NodesCount  # scalar
        ElementsCount = Struct.ElementsCount  # scalar
        IsDOFfree = Struct.IsDOFfree.reshape((-1,))  # [bool] - shape (3*NodesCount,) - support conditions of each DOF
        DOFfreeCount = Struct.DOFfreeCount  # scalar
        C = Struct.C  # the connectivity matrix

        assert NodesCount > 0, "Please check the NodesCount"
        assert ElementsCount > 0, "Please check the ElementsCount"
        assert IsDOFfree.shape == (3 * NodesCount,), "Please check the supports conditions IsDOFfree"
        assert DOFfreeCount > 0, "Please check that at least one degree of freedom is free"
        assert C.shape == (ElementsCount, NodesCount), "Please check that the connectivity matrix C has been computed"

        #1) Initialize the start state for the DR method
        Struct.Start = Struct.StartState(Struct.LoadsToApply,Struct.LengtheningsToApply) # Start state = the Initial State + LoadsToApply + LengtheningsToApply but in the same geometry as before.
        Dt = Struct.DR.Dt #Time increment
        nTimeStep = 0 # t = nTimeStep * Dt

        #2) Compute the residual and the fictitious mass of the start state
        Struct.Start.DRState.UpdateResidualAndMass(Struct,Struct.Start)
        # The tension forces have been computed considering the Initial(=Start).ElementsL and the Start.ElementsLFree (= Initial.ElementsLFree + LengtheningsToApply)
        # The Residual forces have been computed in the Initial(=Start) geometry
        StartRes = Struct.Start.Residual
        StartIsInEquilibrium = Struct.Start.IsInEquilibrium #FYI

        # The Fictitious mass were computed based on the residual and the stiffness Kmat and Kgeo
        # The stiffness matrice Kmat has been computed with the EA/Start.ElementsLFree in the Initial(=Start) geometry
        # The geometric matrice Kgeo has been computed with the Start.tension/Start.ElementsL where all negative tension where reset to 0
        StartMass = Struct.Start.DRState.M

        #3) Compute the initial velocities in t=0:  v(0+Dt/2)  = Dt/2 * Residual/Mass for each DOF
        Struct.Start.DRState.KE = 0 # In the start state t=0, v(0) = 0, hence KE = 0
        Struct.Start.DRState.V = Struct.Start.DRState.Velocities(Struct, Dt/2, StartRes,StartMass) # the velocity at time 0+Dt/2

        #4) Enter the time-incremental method
        nKEReset = 0
        Cur = Struct.Start # the Current State = the starting point of the DR analysis
        Prev = None

        while (nTimeStep<Struct.DR.MaxTimeStep and nKEReset<Struct.DR.MaxKeReset and Cur.IsInEquilibrium == False):

            #4.0) Set the new time: t' = t+Dt
            nTimeStep +=1
            Prev = Cur.Copy()  # the previous state is kept in memory. Prev corresponds to time t
            NewCurState = Prev.Copy()  # a temporary variable.
            Cur = NewCurState # the new current state is a copy of the previous state that need to be updated. Cur corresponds to time t'

            #4.1) Update the velocities : v(t'+Dt/2) = v(t'-Dt/2) + Dt * Residual/Mass with  v(t'-Dt/2) = v(t+Dt/2)
            PrevRes = Prev.Residual
            PrevMass = Prev.DRState.M
            DV = Prev.DRState.Velocities(Struct, Dt, PrevRes, PrevMass)
            Cur.DRState.V = Prev.DRState.V + DV # note that we could have written Cur.DRState.V += DV because the states have been copied

            #4.2) Update the displacements : u(t'=t+Dt) = Dt * v(t'+Dt/2)
            #4.2')Update the nodal coordinates : X(t'= t+Dt) = X(t) + u(t')
            Cur.NodesCoord = Prev.NodesCoord + Dt * Cur.DRState.V

            #4.3) Calculate the current kinetic energy : KE(t'= t+Dt) = 0.5 Mass(t) v(t'+Dt/2) ^2
            Cur.DRState.KE = Cur.DRState.KineticEnergy(Struct, PrevMass, Cur.DRState.V)

            #4.4) Check for energy peak KE(t)>=KE(t')
            if Prev.DRState.KE >= Cur.DRState.KE:  # if KE(t)>=KE(t'), then the Kinetic Energy is decreasing, which means that it has reached a maximum (=Peak) somewhere between t and t'.
                #If Peak, try to estimate the position (=nodesCoord) of the peak. then Reset the velocities to 0 at the position of the peak.
                Peak = Cur.Copy() # lets go back in time at the time of the Peak "t*" (between t and t') and lets estimate the coordinates at t*
                Peak.NodesCoord  = Cur.NodesCoord - 1.5 * Dt * Cur.DRState.V + 0.5 * Dt * DV # see ref [2] eq(7)
                Peak.DRState.UpdateResidualAndMass(Struct,Peak)
                PeakRes = Peak.Residual
                PeakIsInEquilibrium = Peak.IsInEquilibrium #FYI
                PeakMass = Peak.DRState.M
                Peak.DRState.KE = 0
                Peak.DRState.V = Peak.DRState.Velocities(Struct, Dt / 2, PeakRes,PeakMass)  # the velocity at time t*+Dt/2
                Cur = Peak # restart the algorithm from the Peak state
                nKEReset += 1

            #4.5) Update Residual Forces
            #4.6) Update Fictitious Mass
            Cur.DRState.UpdateResidualAndMass(Struct,Cur)
            CurIsInEquilibrium = Cur.IsInEquilibrium #FYI
            #print(CurIsInEquilibrium)

        #Compute the Reaction forces

        Struct.DR.nTimeStep = nTimeStep
        Struct.DR.nKEReset = nKEReset
        Struct.Final = Cur
