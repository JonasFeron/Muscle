import numpy as np
from MusclePy.femodel.fem_structure import FEM_Structure
from MusclePy.femodel.fem_nodes import FEM_Nodes
from MusclePy.femodel.fem_elements import FEM_Elements
from MusclePy.solvers.dr.dr_nodes import DR_Nodes
from MusclePy.solvers.dr.dr_elements import DR_Elements


class DR_Structure(FEM_Structure):
    """
    Extension of FEM_Structure with Dynamic Relaxation specific attributes.
    
    Attributes:
        All attributes from FEM_Structure
        kinetic_energy: Total kinetic energy of the structure
        equilibrium_matrix: Equilibrium matrix computed from elements.connectivity and nodes.coordinates
        global_material_stiffness_matrix: Global material stiffness matrix
        global_geometric_stiffness_matrix: Global geometric stiffness matrix
    """
    
    def __init__(self, structure_or_nodes, elements=None, kinetic_energy=0.0):
        """Initialize a DR_Structure instance.
        
        This constructor accepts either:
        1. A FEM_Structure instance to convert to a DR_Structure instance
        2. A FEM_Nodes (or DR_Nodes) instance and a FEM_Elements (or DR_Elements) instance
        
        Args:
            structure_or_nodes: Either a FEM_Structure instance or a FEM_Nodes (or DR_Nodes) instance
            elements: A FEM_Elements (or DR_Elements) instance, required if structure_or_nodes is a FEM_Nodes instance
            kinetic_energy: Initial kinetic energy of the structure
        """
        # Check if the first argument is a FEM_Structure instance
        if isinstance(structure_or_nodes, FEM_Structure):
            structure = structure_or_nodes
            # Assert that elements is None when a FEM_Structure instance is passed
            assert elements is None, "When passing a FEM_Structure instance, elements must be None"
            
            # Convert nodes and elements to DR types
            dr_nodes, dr_elements = self._convert_to_dr_types(structure.nodes, structure.elements)
                
            # Call parent class constructor with the converted nodes and elements
            super().__init__(dr_nodes, dr_elements)
        else:
            # Assert that the first argument is a FEM_Nodes or DR_Nodes instance
            assert isinstance(structure_or_nodes, (FEM_Nodes, DR_Nodes)), "First argument must be either a FEM_Structure, FEM_Nodes, or DR_Nodes instance"
            # Assert that elements is not None when a FEM_Nodes instance is passed
            assert elements is not None, "When passing a FEM_Nodes instance, elements must not be None"
            
            # Convert nodes and elements to DR types
            dr_nodes, dr_elements = self._convert_to_dr_types(structure_or_nodes, elements)
                
            # Call parent class constructor with the converted nodes and elements
            super().__init__(dr_nodes, dr_elements)
        
        # Initialize DR-specific attributes
        self._kinetic_energy = kinetic_energy
        self._equilibrium_matrix = None
        self._global_material_stiffness_matrix = None
        self._global_geometric_stiffness_matrix = None
    
    def _convert_to_dr_types(self, nodes, elements):
        """Convert nodes and elements to DR_Nodes and DR_Elements types.
        
        This method ensures that:
        1. Nodes are converted to DR_Nodes if not already
        2. Elements are converted to DR_Elements if not already
        3. Elements reference the correct nodes instance
        
        Args:
            nodes: A FEM_Nodes or DR_Nodes instance
            elements: A FEM_Elements or DR_Elements instance
            
        Returns:
            Tuple of (DR_Nodes, DR_Elements) instances
        """
        # Convert nodes to DR_Nodes if not already
        if not isinstance(nodes, DR_Nodes):
            dr_nodes = DR_Nodes(nodes)
        else:
            dr_nodes = nodes
            
        # Convert elements to DR_Elements if not already, ensuring it references the new DR_Nodes
        if not isinstance(elements, DR_Elements):
            dr_elements = DR_Elements(elements)
            # Create a new DR_Elements instance that references the new DR_Nodes
            dr_elements = dr_elements.copy_and_update(nodes=dr_nodes)
        else:
            # If elements are already DR_Elements but nodes were converted,
            # make sure elements reference the new nodes
            if elements.nodes is not dr_nodes:
                dr_elements = elements.copy_and_update(nodes=dr_nodes)
            else:
                dr_elements = elements
                
        return dr_nodes, dr_elements
    
    @property
    def kinetic_energy(self) -> float:
        """Get the total kinetic energy of the structure."""
        return self._kinetic_energy
    
    @property
    def equilibrium_matrix(self) -> np.ndarray:
        """Get the equilibrium matrix."""
        return self._equilibrium_matrix
    
    @property
    def global_material_stiffness_matrix(self) -> np.ndarray:
        """Get the global material stiffness matrix."""
        return self._global_material_stiffness_matrix
    
    @property
    def global_geometric_stiffness_matrix(self) -> np.ndarray:
        """Get the global geometric stiffness matrix."""
        return self._global_geometric_stiffness_matrix
    
    @global_geometric_stiffness_matrix.setter
    def global_geometric_stiffness_matrix(self, value):
        """Set the global geometric stiffness matrix."""
        self._global_geometric_stiffness_matrix = value
    
    def compute_residuals(self):
        """Compute the current state of the structure.
        
        This is a public function to be called once, to avoid recomputing 
        the matrices at each constructor call.
        
        Steps:
        1. Compute local geometric stiffness matrices and axial forces
        2. Compute equilibrium matrix and global stiffness matrices
        3. Compute resisting forces
        4. Compute reactions at supports
        """
        # Compute local geometric stiffness matrices and axial forces
        self.elements.compute_current_state() 

        # Compute equilibrium matrix and global stiffness matrices
        self._compute_matrices()

        # Compute resisting forces
        self._compute_resisting_forces()

        # Compute reactions at supports
        self.nodes.compute_reactions()
    
        # residual forces (loads + reactions - resisting forces) are computed automatically when called
        # see DR_Nodes.residuals (get method)

    def _compute_matrices(self):
        """Compute all matrices based on the current state."""
        from MusclePy.utils.matrix_calculations import (
            compute_equilibrium_matrix,
            compute_global_material_stiffness_matrix,
            local_to_global_matrix
        )
        
        # Compute equilibrium matrix
        self._equilibrium_matrix = compute_equilibrium_matrix(
            self.elements.connectivity,
            self.nodes.coordinates
        )
        
        # Compute global material stiffness matrix
        self._global_material_stiffness_matrix = compute_global_material_stiffness_matrix(
            self.equilibrium_matrix, 
            self.elements.flexibility
        )

        # Compute global geometric stiffness matrix
        self.global_geometric_stiffness_matrix = local_to_global_matrix(
            self.elements.local_geometric_stiffness_matrices,
            self.elements.end_nodes,
            self.nodes.count
        )
    
    def _compute_resisting_forces(self):
        """Compute the resisting forces based on the current state."""
        # Get the equilibrium matrix and element tensions
        A = self.equilibrium_matrix 
        t = self.elements.tension
        
        # Update nodes resisting forces
        self.nodes.resisting_forces = A @ t
    
    def _create_copy(self, nodes, elements, kinetic_energy=None):
        """Core copy method that creates a new instance of the appropriate class.
        
        This protected method is used by all copy methods to create a new instance.
        Child classes should override this method to return an instance of their own class.
        
        Args:
            nodes: A DR_Nodes instance
            elements: A DR_Elements instance
            kinetic_energy: Total kinetic energy of the structure
            
        Returns:
            A new instance of the appropriate class (DR_Structure or a child class)
        """
        ke = self._kinetic_energy if kinetic_energy is None else kinetic_energy
        return self.__class__(nodes, elements, ke)
    
    def copy(self) -> 'DR_Structure':
        """Create a copy of this instance with the current state.
        
        Returns:
            A new instance with the current state
        """
        # Create new nodes with current state
        nodes_copy = self._nodes.copy()
        
        # Create new elements with current state, referencing the new nodes
        elements_copy = self._elements.copy(nodes_copy)       
        return self._create_copy(nodes_copy, elements_copy)
    
    def copy_and_update(self, velocities=None, displacements=None, 
                        loads=None, free_length=None,
                        kinetic_energy=None) -> 'DR_Structure':
        """Create a copy of this instance and update its state.
        
        Args:
            velocity: [m/s] - shape (nodes_count, 3) - Nodal velocities
            displacement: [m] - shape (nodes_count, 3) - Nodal displacements
            loads: [N] - shape (nodes_count, 3) - External loads
            free_length: [m] - shape (elements_count,) - free length
            kinetic_energy: [J] - Total kinetic energy
            
        Returns:
            A new instance with the updated state
        """
        # Create new nodes with updated state
        nodes_copy = self.nodes.copy_and_update(
            loads=loads,
            displacements=displacements,
            velocities=velocities
        )
        
        # Create new elements with updated state, referencing the new nodes
        elements_copy = self.elements.copy_and_update(
            nodes=nodes_copy, 
            free_length=free_length
        )
        
        # Create a new DR_Structure with the updated nodes and elements
        return self._create_copy(nodes_copy, elements_copy, kinetic_energy)
    
    def copy_and_add(self, loads_increment=None, free_length_variation=None) -> 'DR_Structure':
        """
        Create a copy of the current state and add loads and/or free length increments.
        
        Args:
            loads_increment: [N] - shape (dof,) - Loads increment to add
            free_length_variation: [m] - shape (elements_count,) - Free length increment to add
            
        Returns:
            DR_Structure: New state with added loads and/or free length increments
        """
        loads_increment = self.nodes._check_and_reshape_array(loads_increment, "loads_increment")
        free_length_variation = self.elements._check_and_reshape_array(free_length_variation,"free_length_variation")  
        
        # Create new nodes with updated loads
        nodes_copy = self.nodes.copy_and_update(
            loads=self.nodes.loads + loads_increment
        )
        
        # Create new elements with updated free_length_variation
        elements_copy = self.elements.copy_and_update(
            nodes=nodes_copy,
            free_length=self.elements.free_length + free_length_variation
        )
        
        # Create a new DR_Structure with the updated nodes and elements
        return self._create_copy(nodes_copy, elements_copy)
