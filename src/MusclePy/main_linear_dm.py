import numpy as np


def main(nodes, elements):
    """
    Main function to solve linear displacement problem using Python.NET
    
    Args:
        nodes (FEM_Nodes): Nodes data from C#
        elements (FEM_Elements): Elements data from C#
    
    Returns:
        FEM_NodesResults, FEM_ElementsResults: Results for nodes and elements
    """
    # Convert input data to numpy arrays for computation
    nodes_coord = np.array(nodes.NodesCoord)
    loads_init = np.array(nodes.LoadsInit)
    loads_to_apply = np.array(nodes.LoadsToApply)
    is_dof_free = np.array(nodes.IsDOFfree)
    
    elements_end_nodes = np.array(elements.ElementsEndNodes)
    elements_a = np.array(elements.ElementsA)
    elements_e = np.array(elements.ElementsE)
    tension_init = np.array(elements.TensionInit)
    
    # Create structure object and perform calculations
    struct = StructureObj()
    struct.nodes_coord = nodes_coord
    struct.loads_init = loads_init
    struct.loads_to_apply = loads_to_apply
    struct.is_dof_free = is_dof_free
    struct.elements_end_nodes = elements_end_nodes
    struct.elements_a = elements_a
    struct.elements_e = elements_e
    struct.tension_init = tension_init
    
    # Perform linear displacement analysis
    struct.linear_displacement_method()
    
    # Create results objects
    nodes_results = FEM_NodesResults()
    nodes_results.NodesCoord = struct.nodes_coord
    nodes_results.ReactionsInit = struct.reactions_init
    
    elements_results = FEM_ElementsResults()
    elements_results.Tension = struct.tension
    elements_results.IsInEquilibrium = struct.is_in_equilibrium
    
    return nodes_results, elements_results

def core(nodes, elements):
    """Wrapper function to maintain compatibility with existing code"""
    return main(nodes, elements)

        def CoreLinearDisplacementMethod(Self):
        """
                Perform the Linear Displacement Method on the Start State of the Structure.
                This method assumes that the StructureObject has already been initialized with InitialData method
                :return: The final State of the structure in Equilibrium
                """

        # 0) Check inputs
        NodesCount = Self.NodesCount  # scalar
        ElementsCount = Self.ElementsCount  # scalar
        IsDOFfree = Self.IsDOFfree.reshape((-1,))  # [bool] - shape (3*NodesCount,) - support conditions of each DOF
        DOFfreeCount = Self.DOFfreeCount  # scalar
        C = Self.C  # the connectivity matrix

        assert NodesCount > 0, "Please check the NodesCount"
        assert ElementsCount > 0, "Please check the ElementsCount"
        assert IsDOFfree.shape == (3 * NodesCount,), "Please check the supports conditions IsDOFfree"
        assert DOFfreeCount > 0, "Please check that at least one degree of freedom is free"
        assert C.shape == (ElementsCount, NodesCount), "Please check that the connectivity matrix C has been computed"

        # 1) Initialize the start state for the Displacement method
        Self.Start = Self.StartState(Self.LoadsToApply,Self.LengtheningsToApply)  # Start state = the Initial State + LoadsToApply + LengtheningsToApply but in the same geometry as before.
        Self.Start.ElementsE = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsE) #select the young modulus EinCompression for struts or EinTension for cables
        Self.Start.ElementsA = Self.ElementsInTensionOrCompression(Self.ElementsType, Self.ElementsA)
        (PrestressForces,PrestressLoads) = Self.Start.PrestressLoads(Self,Self.LengtheningsToApply,Self.Start.ElementsE,Self.Start.ElementsA,Self.Start.ElementsLFree)
        Self.Start.Loads += PrestressLoads
        Self.Start.Loads -= Self.Initial.Loads # only apply the additionnal load on the structure and not the one that were already there before

        start = Self.Start

        # 2) Solve the linear system of equations K*d=Flex

        perturb = 1e-5  # [m], à appliquer si matrice singulière uniquement

        d = np.zeros((3 * Self.NodesCount, ))
        Tension = np.zeros((Self.ElementsCount, ))
        Reactions = np.zeros((Self.FixationsCount, ))

        try:
            (d, Tension, Reactions) = start.LinearDisplacementMethod(Self,start.NodesCoord, Self.Initial.Tension, start.Loads, start.ElementsE, start.ElementsA, start.ElementsLFree)
        except np.linalg.LinAlgError:
            # print("la matrice est singulière")
            NodesCoord_perturbed = Self.Perturbation(start.NodesCoord, Self.IsDOFfree, perturb)
            (d, Tension, Reactions) = start.LinearDisplacementMethod(Self,NodesCoord_perturbed, Self.Initial.Tension, start.Loads, start.ElementsE, start.ElementsA, start.ElementsLFree)

        finally:
            # In Linear calculation, the equilibrium is achieved in the initial state. The final state is the deformed geometry
            Self.Start.Tension = Tension + PrestressForces
            Self.Start.Loads -= PrestressLoads #prestress loads are fictive
            Self.Start.Reactions = Reactions

            Self.Final = Self.Start.Copy()
            Self.Final.Loads += Self.Initial.Loads  # total loads applied on the structure
            Self.Final.NodesCoord = start.NodesCoord + d
            (Self.Final.ElementsL, Self.Final.ElementsCos) = Self.Final.ElementsLengthsAndCos(Self,Self.Final.NodesCoord)
            (Self.Final.A, Self.Final.AFree, Self.Final.AFixed) = Self.Final.EquilibriumMatrix(Self,Self.Final.ElementsCos)
            Self.Final.Residual = Self.Final.UnbalancedLoads(Self, Self.Final.AFree, Self.Final.Loads,Self.Final.Tension)



def Perturbation(Self,NodesCoord,IsDOFfree,perturb):
        """
        Apply a perturbation on all nodes free in Z
        :return: NodesCoord_perturbed: vecteur (Nx3) des coordonnées des noeuds avec perturbation
        """
        NodesCoord_perturbed = NodesCoord.copy().reshape((-1,3))
        IsZfree = IsDOFfree.reshape((-1,3))[:,2]
        NodesCoord_perturbed[IsZfree,2] -= perturb
        return NodesCoord_perturbed.reshape((-1,))
    