import numpy as np

from MusclePy.twin_model.twin_elements_results import Twin_ElementsResults


class Elements_State (Twin_Elements):
    def __init__(self, twin_element=None,nodes_state=None, previous_action=None, previous_result=None):
        
        assert twin_element is not None, "impossible to construct an elements_state instance"
        assert nodes_state is not None, "impossible to construct an elements_state instance without nodes_state"

        super.__init__(twin_element.type, twin_element.end_nodes, twin_element.initial_free_lengths)

        # # [mm²] - shape (ElementsCount, 1) - Areas, depending whether the elements are in Compression or in Tension
        # self.areas = np.array(areas, dtype=float) if areas is not None else np.array([]) 

        # # [MPa] - shape (ElementsCount, 1) - Young Moduli, depending whether the elements are in Compression or in Tension
        # self.young_moduli = np.array(young_moduli, dtype=float) if young_moduli is not None else np.array([]) 

        # # # shape (ElementsCount, ) - Free Length of the Elements 
        # self.free_lengths = np.array(free_lengths, dtype=float) if free_lengths is not None else np.array([])  

        self.result  = previous_result if previous_result is not None else Twin_ElementsResults()

    def get_current_area(previous_result):


    def get_current_property(Self, TensionValue, PropertyInCompressionAndTension):
        """
        Select the property of the element depending on if it is in tension or in compression
        :param TensionValue: [any unit] - shape (ElementsCount,) - Any value >= O is considered as tension. It can be force, strain, elongation, stress,...
        :param PropertyInCompressionAndTension: [any unit] - shape (ElementsCount,2) - The properties [InCompression,InTension] of each element. It can be the Area or Young modulus.
        :return: Property: [any unit] - shape (ElementsCount,) - The properties of each element depending if the element is in tension or in compression.
        """

        assert PropertyInCompressionAndTension.shape == (Self.ElementsCount, 2), "Please check the shape of the PropertiesInCompression_Tension"

        # 2) Check the state of the elements (in compression or in tension) and find their associated stiffness

        # For each elements, there is one E value in case of compression and another value in case of tension. Idem for A
        # For instance, the Young modulus of a cable could be 0 in compression and 100e3 MPa in tension.
        # In this case, the cable vanish from stiffness matrix if it slacks

        PropertyInCompression = PropertyInCompressionAndTension[:, 0]
        PropertyInTension = PropertyInCompressionAndTension[:, 1]

        IsElementInTension = TensionValue > 0  # a vector where the entry i is true if the element is in tension, and false if it is in compression
        Property = np.where(IsElementInTension, PropertyInTension, PropertyInCompression)  # the property of the elements depending if compression or tension

        #IF the tension in the element is 0, then choose the property according to the type (strut or cable) of the element
        BasedOnType = TensionValue==0 # a vector where the entry i is true if the property of the element is computed based on his type.
        types = Self.ElementsType[BasedOnType] #-1 if struts, 1 if cables, but only for the elements without tension
        PropertyCables = PropertyInTension[BasedOnType]
        PropertyStruts = PropertyInCompression[BasedOnType]
        Property[BasedOnType] = np.where(types > 0, PropertyCables, PropertyStruts)

        return Property

    def Flexibility(Self, ElementsE, ElementsA, ElementsL):
        """
        Returns the flexibility L/EA of the elements (considering a possible infinite flexibility = no stiffness)
        :param Struct: The StructureObject in the current state
        :param ElementsE: [N/mm²] - shape (ElementsCount,) - The young modulus of the elements.
        :param ElementsA: [mm²] - shape (ElementsCount,) - The area of the elements.
        :param ElementsL: [m] - shape (ElementsCount,) - The lengths (free or current) of the elements.
        :return: Flex : [m/N] - shape (ElementsCount,) - The flexibility L/EA of the elements.
        """
        # 0) Check the inputs
        assert ElementsE.size == Self.ElementsCount, "Please check the shape of ElementsE"
        assert ElementsA.size == Self.ElementsCount, "Please check the shape of ElementsA"
        assert ElementsL.size == Self.ElementsCount, "Please check the shape of ElementsL"
        E = ElementsE.reshape(-1, ).copy()
        A = ElementsA.reshape(-1, ).copy()
        L = ElementsL.reshape(-1, ).copy()

        # 1) Find the slack clables, they have a 0 stiffness, hence infinite flexibility

        NoStiffnessElementsIndex = np.where(np.logical_or(E <= 1e-4, A <= 1e-4))

        A[NoStiffnessElementsIndex] = 1  # to avoid to divide by 0 later
        E[NoStiffnessElementsIndex] = 1  # to avoid to divide by 0 later

        # 2) Compute the flexibility
        F = L / (E * A)
        F[NoStiffnessElementsIndex] = 1e9  # [m/N] elements with 0 stiffness have an infinite flexibility
        return F

        
    def ConnectivityMatrix(Self, NodesCount, ElementsCount, ElementsEndNodes):
        """
        :return: the connectivity matrix C of shape (ElementsCount, NodesCount). C contains the same info than ElementsEndNodes but presented under a matrix form.
        """

        #Calculation according to references
        # Vassart, Motro, 1999, Multiparametered Formfinding Method: Application to Tensegrity Systems
        # Sheck, 1974, The force density method for formfinding and computation of networks

        C = np.zeros((ElementsCount, NodesCount), dtype=int)  # connectivity matrix C
        for line_ind, line_extremities in enumerate(ElementsEndNodes):
            n0 = line_extremities[0]
            n1 = line_extremities[1]
            C[line_ind, n0] = 1
            C[line_ind, n1] = -1

        return -C  #- signe because it makes more sense to do n1-n0 (than n0-n1) when computing a cosinus (X1-X0)/L01. But this actually does not change the equilibrum matrix.
        # print(C)