# Muscle for developers

## Introduction
### Overview

Muscle is a structural analysis plugin for Grasshopper designed with a clean, modular architecture that separates concerns and promotes maintainability, testability, and extensibility. 

The plugin leverages a dual-language approach:
- **C#**: Used for Grasshopper components
- **Python**: Implements the finite element methods of structural analysis
- **[Python.NET](https://www.nuget.org/packages/pythonnet)**: Enables the use of Python libraries inside C# code. (Note: In the early years of Muscle, [PythonConnect](https://www.nuget.org/packages/PythonConnect) was used instead of Python.NET.)

This combination takes advantage of C#'s strong UI (User Interface) capabilities and integration with Grasshopper, while leveraging Python's scientific computing ecosystem and mathematical libraries for efficient structural analysis.

### Purpose of This Documentation

This README is written to invite and guide developers interested in collaborating on Muscle's development. It provides an overview of the software architecture and explains key design patterns. By understanding these principles, contributors can effectively extend and improve the Muscle library while maintaining its architectural integrity.

### Join the Muscle Development Community

We welcome contributors with diverse backgrounds and skill sets to join the Muscle development community. Whether you're experienced in structural engineering, software development, or just interested in learning, there's a place for you in this project.

As you explore Muscle's codebase, these resources might be helpful:

- For **Grasshopper Development**: The [Rhino Developer Documentation](https://developer.rhino3d.com/en/guides/grasshopper/) provides excellent guidance on grasshopper plugin development
- For **C# Programming**: The codebase uses object-oriented principles that are well-documented in many online resources
- For **Python and Scientific Computing**: Familiarity with NumPy and SciPy can help you understand the computational core

Don't hesitate to ask questions, propose improvements, suggest new features, or make contributions - we welcome your input!

## Muscle Software Architecture
### Overview of the Layered Architecture

The codebase is organized into four main layers (Muscle, MuscleApp, MuscleCore, MusclePy), which may be visualized in the following form:

```
                      Muscle (User Interface)        
        ╔══════════════════════════════════════╗     
        ║             MuscleApp                ║     
        ║   ╔════════════════════════════╗     ║     
        ║   ║         MuscleCore         ║     ║     
        ║   ║   ╔══════════════════╗     ║     ║     
input ->║ ->║ ->║     MusclePy     ║ ->  ║ ->  ║ ->  output
        ║   ║   ╚══════════════════╝     ║     ║     
        ║   ╚════════════════════════════╝     ║     
        ╚══════════════════════════════════════╝     

```
Figure 1: Representation of a Muscle "solver" component on the Grasshopper canvas 

The outermost box shown in Figure 1 represents a Grasshopper component, which is visible by the user on the Grasshopper canvas. Inside this component, other functions are nested, each performing a specific task without knowledge of the users. The grasshopper components are written in C# using the [official Grasshopper Template](https://developer.rhino3d.com/guides/grasshopper/simple-component/). MuscleApp and MuscleCore layers are also written in C#, while MusclePy is written in Python.  

Let's consider the following example to progressively decrypt the software architecture. Suppose the outermost box represents a grasshopper component called "Solver by linear displacement method". On the left, it takes a grasshopper tree of external Loads to apply on the structure, and on the right, it returns a grasshopper tree of new nodal coordinates after displacements. The nodal coordinates are of native grasshopper type [GH_Point](https://developer.rhino3d.com/api/grasshopper/html/T_Grasshopper_Kernel_Types_GH_Point.htm), while external loads are custom  [Grasshopper Data Type](https://developer.rhino3d.com/guides/grasshopper/grasshopper-data-types/) defined in Muscle. 

In the innermost box "MusclePy", no longer on the grasshopper canvas but in Python, the structural analysis actually takes place. MusclePy is called from the core of the grasshopper component. MusclePy's responsibility is to efficiently solve matricial equations (e.g., `K·d = F` where K is the stiffness matrix, d is the displacement array, and F is the load array) using NumPy's optimized numerical library. Importantly, Python has no knowledge of Grasshopper-specific data structures like data trees, branches, and native or custom grasshopper types. Python only deals with loads and displacements as numpy arrays of numbers.

This clean separation of concerns requires data to be progressively converted and transferred as it moves from left to right through the architectural layers. The architecture ensures that each layer has a single responsibility and that the data is transformed in a way that is meaningful to the next layer. The advantages of this approach include:

1. **Language Optimization**: Each language is used for what it does best - C# for UI and object-oriented programming, Python for numerical computation.

2. **Modularity**: Each layer can be developed, tested, and maintained independently, reducing complexity and increasing robustness. 

3. **Flexibility**: The implementation of any layer can be changed without affecting the others. In other words, the migration from Grasshopper 1 to Grasshopper 2 should be possible one day, without having to restart everything from scratch.

4. **Testability**: Each layer can be tested in isolation, making it easier to identify and fix bugs. No need to launch Rhino/Grasshopper to test the Python core computations, nor to test the Python.NET data conversion between C# and Python.

5. **Scalability**: New features can be added to specific layers without affecting the entire system.

6. **Performance**: The computational core in Python can leverage highly optimized numerical libraries like NumPy, SciPy, and other scientific computing tools.

7. **Maintainability**: Clear separation of concerns makes the codebase easier to understand and maintain over time.

### MVVM pattern and Grasshopper data types

Muscle's Grasshopper plugin is organized according to the Model-View-ViewModel ([MVVM](https://en.wikipedia.org/wiki/Model%E2%80%93view%E2%80%93viewmodel)) pattern. 

This separation allows each layer to focus on its specific responsibilities:
- The **Model** is the Finite Element Model (FEM) focusing on structural analysis. 
- The **View** focuses on visualization in Rhino
- The **ViewModel** is the intermediary between the Model and View. It is a representation of the Model that can be manipulated by the user. 

For instance, the custom PointLoad object demonstrates the MVVM pattern clearly:
- In the **Model**, the external loads are a numpy array of numbers, representing the load value for each degree of freedom (for each node and each direction X,Y,Z).
- In the **View**, external loads can be previewed in the Rhino viewport as a green arrow. This green arrow is defined by the GH_PointLoad class. GH_PointLoad is a custom [Grasshopper Data Type](https://developer.rhino3d.com/guides/grasshopper/grasshopper-data-types/). It also defines some functionnalities to view the loads data on the Grasshopper canvas.  
- In the **ViewModel**, the external loads are an instance of a PointLoad object. Multiple PointLoads can be defined by the user, such as the self-weight or external loads in the X, Y or Z directions. Each PointLoad is wrapped in a GH_PointLoad object for **visualization** in Rhino and Grasshopper. When feeding a grasshopper tree of GH_PointLoad to a solver component, all PointLoads are summed up and converted to a single numpy array of numbers in the **Model**.

### MVVM in the layered architecture

The MVVM pattern is clearly visible and integrated inside the layered architecture (i.e. folder structure):

```
src/  
├── Muscle/                  # User Interface layer 
│   ├── View/                # GH_data types (e.g. loads as GH_PointLoad type for visualization)  
│   ├── Components/          # Construction of Grasshopper Components
│   ├── Converters/          # Data conversion with MuscleApp layer
│   └── ...  
├── MuscleApp/               # Application layer 
│   ├── ViewModel/           # custom data types (e.g. loads as PointLoad type)  
│   ├── Solvers/             # logic inside the "Solver" Grasshopper components  
│   ├── Converters/          # Data conversion with MuscleCore layer
│   └── ...  
├── MuscleCore/              # Core layer
│   ├── FEModel/             # C# finite element model (e.g. loads as C# arrays)  
│   ├── Solvers/             # Core C# solvers calling Python solvers  
│   ├── Converters/          # Data conversion with MusclePy layer
│   └── ...  
├── MusclePy/                # Core layer for computations  
│   ├── femodel/             # Python finite element model (e.g. loads as Numpy arrays)  
│   ├── solvers/             # Actual solvers
│   └── utils/               # tools for matrix computations  
└── README.md                # This documentation file  
```
### Data Flow through the layered architecture
To describe the software architecture with concrete terms, consider Figure 2, which illustrates how data flows through the different layers of the architecture. Figure 2 further details the example of Figure 1, from the grasshopper component visible on the canvas to the Python solver.

```
[Grasshopper Canvas]
grasshopper tree of GH_PointLoad  ──────>    "Solver" Component  ──────> new nodal coordinates as grasshopper tree of GH_Point 
                         │                                                                                              ▲
                         │                                                                                              │
[MuscleApp]              ▼                                                                                              │
            list of PointLoad     ──────>    MuscleApp Solver    ──────> new nodal coordinates as             list of Point3d
                         │                                                                                              ▲
                         │                                                                                              │
[MuscleCore]             ▼                                                                                              │
loads as C# arrays of numbers    ──────>    MuscleCore Solver    ──────> displacements as                C# arrays of numbers
                         │                                                                                              ▲
                         │                                                                                              │
[MusclePy]               ▼                                                                                              │
loads as numpy arrays of numbers ──────>  solve loads = K*displacements  ──────> displacements as     numpy arrays of numbers
```
**Figure 2: Data conversion flow through architectural layers**

In Figure 1, each time data crosses from left to right a double line || representing a box, a data conversion takes place. In Figure 2, this corresponds to a change of layer (vertical arrows). In the folder structure, this conversion is handled by the Converters folder. 

For example, as soon as the data enters the grasshopper component, a first data conversion already takes place: The GH_PointLoad object drops its visualization properties (e.g. color, size) and only the PointLoad values are kept in the MuscleApp layer. 
While the [Grasshopper Components](https://developer.rhino3d.com/guides/grasshopper/simple-component/) are built in the first User Interface layer "Muscle", the logic of the components is actually defined in the second layer MuscleApp. This way, the component logic (what happens inside the SolveInstance method of the component) is decoupled from its construction (where input and output are defined). This allows for a proper encapsulation of the code, and separation of concerns.

Another example can be seen on the MuscleCore layer. This layer sole responsibility is to transfer data between C# and Python, managing the Python.NET engine and ensuring smooth communication between the two languages ([through appropriate converters](https://github.com/pythonnet/pythonnet/wiki/Codecs:-customizing-object-marshalling-between-.NET-and-Python)). 

This progressive transformation ensures that each layer works with data in the format most appropriate for its responsibilities, while maintaining the clean separation between layers. 

### Dependency Flow

An important aspect of this architecture is how dependencies flow between layers. Following the principles of clean architecture:

1. **Dependencies flow inward**: Outer layers depend on inner layers, but inner layers never depend on outer layers.
   - Muscle (UI & View) → MuscleApp (ViewModel) → MuscleCore (C# Model) → MusclePy (Python Computations)
   - This ensures that the most critical code (computational core) has the fewest dependencies

2. **Concrete Dependencies**:
   - Muscle depends on Grasshopper and MuscleApp. It uses [Grasshopper API](https://developer.rhino3d.com/api/grasshopper/html/723c01da-9986-4db2-8f53-6f3a7494df75.htm). 
   - MuscleApp depends on Grasshopper and MuscleCore. It uses [Rhino.Geometry API](https://developer.rhino3d.com/api/rhinocommon/rhino.geometry?version=7.x). It has no direct knowledge of Python.NET and MusclePy. 
   - MuscleCore solely depends on Python.NET to use, from C#, the Python library "MusclePy". It has no knowledge of Grasshopper.
   - MusclePy depends on NumPy and SciPy for numerical computations. It has no knowledge of Grasshopper, nor Python.NET. It may be used completely independently from C#. It may be used by other applications. 

### C# = Onion Architecture ?
In conclusion, the C# portion (Muscle -> MuscleApp -> MuscleCore) of the codebase seems to follow a classic [Onion architecture](https://medium.com/@alessandro.traversi/understanding-onion-architecture-an-example-folder-structure-9c62208cc97d) with:
- Core domain at the center (MuscleCore)
- Application services in the middle layer (MuscleApp)
- UI/presentation at the outer layer (Muscle Grasshopper components and View)

However, in an Onion architecture, the core domain contains the business logic, which is not the case here since MuscleCore does not contain any structural analysis logic. Hence the term "Hexagonal Architecture" seems more appropriate, as described next. 

### C# + Python = Hexagonal Architecture 
In conclusion, the complete (C# + Python) codebase (Muscle -> MuscleApp -> MuscleCore -> MusclePy) follows the principles of [Hexagonal Architecture](https://miladezzat.medium.com/hexagonal-architecture-ports-and-adapters-pattern-5ad2421802ec) (with Ports and Adapters) :

 - MuscleCore does not contain any structural analysis logic, but just raw model data. 
 - MuscleCore only serves as data containers ready to be shipped to Python via [Python.NET](https://www.nuget.org/packages/pythonnet) ports. 
 - MuscleCore also implements the appropriate [Python.NET converters](https://github.com/pythonnet/pythonnet/wiki/Codecs:-customizing-object-marshalling-between-.NET-and-Python) that allow the data to be transferred between the two languages. 


## Summary: 

Muscle is a dual-language software with:

- **C# code**: for the 3 layers "Muscle", "MuscleApp", and "MuscleCore" (of the grasshopper plug-in)
- **Python code**: for the "MusclePy" library (of structural analysis)

The organization follows the MVVM (Model-View-ViewModel) pattern:
- **View**: In the first layer, Muscle defines how the data are displayed on the grasshopper canvas and in the Rhino Viewport. Muscle also builds the User Interface through Grasshopper components.
- **ViewModel**: In the second layer, MuscleApp mediates between the UI and the Finite Element Model
- **Model**: In the third and fourth layer, the finite element model is twinned between MuscleCore and MusclePy. MuscleCore in C# contains the raw model data, while MusclePy in Python performs the structural analysis.

While the C# side is organized in a layered Onion architecture, there's an important distinction: MuscleCore doesn't contain the actual business logic as would be typical in a pure Onion architecture. Instead, MuscleCore primarily serves as a data container to be shipped to Python via Python.NET ports. The core structural analysis logic resides in MusclePy.

This creates a hexagonal architecture where:
- The **port** is [Python.NET](https://www.nuget.org/packages/pythonnet), who allows the two languages to communicate. 
- The **adapters** are the converters implemented in MuscleCore, which transform the finite element model data between the two languages (from C# arrays to Python numpy arrays, and vice versa)

This choice of architecture allows each language to focus on its strengths while maintaining a clean separation of concerns.

The result is a flexible, maintainable, testable, and extensible software that leverages C#'s UI capabilities and object-oriented design alongside Python's powerful numerical computing libraries.
