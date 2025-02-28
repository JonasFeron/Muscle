import numpy as np
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.solvers.linear_dm.structure_state_4linear_dm import Structure_State_4Linear_DM
from femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_structure_results import FEM_Structure_Results

def main_linear_displacement_method(structure:FEM_Structure) -> FEM_Structure_Results:
    """

    :param structure:
    :return:
    """

    start = Structure_State_4Linear_DM(structure.nodes, structure.elements, structure.applied, structure.nodes_results, structure.elements_results)

    additional_loads = structure.additional.loads  
    additional_lengthenings = structure.additional.delta_free_lengths

    results = FEM_Structure_Results()

        # (PrestressForces,PrestressLoads) = Self.Start.PrestressLoads(Self,Self.LengtheningsToApply,Self.Start.ElementsE,Self.Start.ElementsA,Self.Start.ElementsLFree)
        # Self.Start.Loads += PrestressLoads


        # 2) Solve the linear system of equations K*d=Flex

        perturb = 1e-5  # [m], à appliquer si matrice singulière uniquement

        d = np.zeros((3 * Self.NodesCount, ))
        Tension = np.zeros((Self.ElementsCount, ))
        Reactions = np.zeros((Self.FixationsCount, ))

        try:
            (d, Tension, Reactions) = linear_displacement_method(start, additional_loads)
        except np.linalg.LinAlgError:
            # print("la matrice est singulière")
            NodesCoord_perturbed = Self.Perturbation(start.NodesCoord, Self.IsDOFfree, perturb)
            (d, Tension, Reactions) = linear_displacement_method(start, additional_loads)

        finally:
            # In Linear calculation, the equilibrium is achieved in the initial state. The final state is the deformed geometry
            # Self.Start.Tension = Tension + PrestressForces
            # Self.Start.Loads -= PrestressLoads #prestress loads are fictive
            # Self.Start.Reactions = Reactions

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
    