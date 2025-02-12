
//this file is based on the template https://github.com/JonasFeron/PythonNETGrasshopperTemplate 
//------------------------------------------------------------------------------------------------------------

//PythonNETGrasshopperTemplate

//Copyright <2025> <Jonas Feron>

//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.

//List of the contributors to the development of PythonNETGrasshopperTemplate: see NOTICE file.
//Description and complete License: see NOTICE file.

//this file was imported from https://github.com/JonasFeron/PythonConnectedGrasshopperTemplate and is used WITH modifications.
//------------------------------------------------------------------------------------------------------------

//Copyright < 2021 - 2025 > < Université catholique de Louvain (UCLouvain)>

//Licensed under the Apache License, Version 2.0 (the "License");
//you may not use this file except in compliance with the License.
//You may obtain a copy of the License at

//    http://www.apache.org/licenses/LICENSE-2.0

//Unless required by applicable law or agreed to in writing, software
//distributed under the License is distributed on an "AS IS" BASIS,
//WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
//limitations under the License.

//List of the contributors to the development of PythonConnectedGrasshopperTemplate: see NOTICE file.
//Description and complete License: see NOTICE file.
//------------------------------------------------------------------------------------------------------------


using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Muscle.Elements;
using Muscle.Loads;
using Muscle.Nodes;
using Muscle.PythonLink;
using Muscle.PythonNETComponents.TwinObjects;
using Muscle.Structure;
using Newtonsoft.Json;
using Python.Runtime;

namespace Muscle.Solvers
{
    public class LinearSolverDisplComponent : GH_Component
    {

        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public LinearSolverDisplComponent()
          : base("Solver - Linear - Displacements Meth.", "Linear D",
                "Solve truss.\n" +
                "  Displacement method is used (solve K.U=L then post-process to find axial forces)",
              "Muscles", "Solvers")
        {
        }

        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override System.Drawing.Bitmap Icon
        {
            get
            {
                //You can add image files to your project resources and access them like this:
                // return Resources.IconForThisComponent;
                return null;
            }
        }

        /// <summary>
        /// Gets the unique ID for this component. Do not change this ID after release.
        /// </summary>
        public override Guid ComponentGuid
        {
            get { return new Guid("2ec0d860-6029-4346-8925-49f2c69e132c"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure which may contain previous results (forces and displacements).", GH_ParamAccess.item);
            pManager.AddGenericParameter("External Point Loads", "Le (kN)", "The external point loads to apply on the structure.", GH_ParamAccess.tree);
            pManager.AddGenericParameter("Length Variation", "DL (m)", "Lengthening (+) or shortening (-) to apply on the elements.", GH_ParamAccess.tree);
            pManager[1].Optional = true;
            pManager[2].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {
            pManager.AddGenericParameter("Structure", "struct", "A structure containing the results (forces and displacements).", GH_ParamAccess.item);

        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            string pythonScript = AccessToAll.MainLinearSolve; // ensure that the python script is located in AccessToAll.pythonProjectDirectory, or provide the relative path to the script.
            if (!AccessToAll.hasPythonStarted)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Python has not been started. Please start the 'StartPython.NET' component first.");
                return;
            }
            if (!File.Exists(Path.Combine(AccessToAll.pythonProjectDirectory, pythonScript)))
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"Please ensure that \"{pythonScript}\" is located in: {AccessToAll.pythonProjectDirectory}");
                DA.SetData(0, null);
                return;
            }

            //1) Collect Data
            StructureObj structure = new StructureObj();
            GH_Structure<IGH_Goo> gh_loads_ext = new GH_Structure<IGH_Goo>();
            GH_Structure<IGH_Goo> gh_loads_prestress = new GH_Structure<IGH_Goo>();
            //int n_it = -1;

            if (!DA.GetData(0, ref structure)) { return; }
            if (!DA.GetDataTree(1, out gh_loads_ext)) { }
            if (!DA.GetDataTree(2, out gh_loads_prestress)) { }
            //if (!DA.GetData(3, ref n_it)) { return; }


            //2) Transform datas before solving in python
            StructureObj new_structure = structure.Duplicate(); //a) Duplicate structure to not alter the original

            bool success1 = RegisterPointLoads(new_structure, gh_loads_ext.FlattenData());
            bool success2 = RegisterPrestressLoads(new_structure, gh_loads_prestress.FlattenData());

            if (!success1 && !success2)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to collect load data");
                return; //abort if both failed
            }
            //3) Solve in python



            SharedData data = new SharedData(new_structure); //Object data contains all the essential informations of structure
            SharedSolverResult result = new SharedSolverResult();

            string jsonData = JsonConvert.SerializeObject(data, Formatting.None);
            dynamic jsonResult = null;

            //2) Solve in python
            var m_threadState = PythonEngine.BeginAllowThreads();

            // following code is inspired by https://github.com/pythonnet/pythonnet/wiki/Threading
            using (Py.GIL())
            {
                try
                {
                    dynamic script = PyModule.Import(pythonScript);
                    dynamic mainFunction = script.main;
                    jsonResult = mainFunction(jsonData);
                    JsonConvert.PopulateObject((string)jsonResult, result);
                }
                catch (PythonException ex)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, ex.Message);
                }
                catch (Exception e)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, e.Message);
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, $"python result= {jsonResult}");
                    return;
                }
            }
            PythonEngine.EndAllowThreads(m_threadState);

            new_structure.PopulateWithSolverResult(result);

            GH_StructureObj gh_structure = new GH_StructureObj(new_structure);
            DA.SetData(0, gh_structure);
        }

        private bool RegisterPointLoads(StructureObj new_structure, List<IGH_Goo> datas)
        {
            //return true if at least one load is added on the structure
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            //new_structure.LoadsToApply = new List<Vector3d>();
            //foreach (var node in new_structure.StructuralNodes) new_structure.LoadsToApply.Add(new Vector3d(0.0, 0.0, 0.0)); // initialize the LoadsToApply vector with 0 load for each DOF. 


            List<Node> nodes = new_structure.StructuralNodes; //use a shorter nickname 

            PointLoad load;
            foreach (var data in datas)
            {
                if (data is GH_PointLoad)
                {
                    load = ((GH_PointLoad)data).Value; //retrieve the pointload inputted by the user

                    // we need to know on which point or node the load will have to be applied
                    int ind = -1;
                    if (load.NodeInd != -1) //PointsLoad can be defined on a point or on a node index
                    {
                        ind = load.NodeInd;
                    }
                    else // load may have been defined on a point not on a node
                    {
                        if (!Node.EpsilonContains(nodes, load.Point, new_structure.ZeroTol, out ind)) //try to find the point between all nodes
                        {
                            AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "A point Load is applied on a point which does not belong to the structure. This point load is ignored.");
                            continue;//go to next point load
                        }
                    }
                    new_structure.LoadsToApply[ind] += load.Vector; //If Point Load is applied on a node of the structure, then the load is added to all the Loads to apply on the structure. 
                    success = true;
                }
            }
            return success;
        }

        private bool RegisterPrestressLoads(StructureObj new_structure, List<IGH_Goo> datas)
        {
            bool success = false;
            if (datas.Count == 0 || datas == null) return false; //failure and abort

            //new_structure.LengtheningsToApply = new List<double>();
            //foreach (var elem in new_structure.StructuralElements) new_structure.LengtheningsToApply.Add(0.0); // initialize the LengtheningsToApply vector with 0m length change for each element. 

            //List<Node> nodes = new_structure.StructuralNodes;
            List<Element> elements = new_structure.StructuralElements;

            ImposedLenghtenings DL;
            foreach (var data in datas)
            {
                if (data is GH_ImposedLengthenings)
                {
                    DL = ((GH_ImposedLengthenings)data).Value; //the prestressload is a variation of length

                    int ind_e = DL.Element.Ind;

                    new_structure.LengtheningsToApply[ind_e] += DL.Value; //The variation of length is added to the force to all the lengthenings to apply on the structure. 
                    success = true;
                }
            }
            return success; // if at least one lengthening will be applied on the structure
        }
    }
}