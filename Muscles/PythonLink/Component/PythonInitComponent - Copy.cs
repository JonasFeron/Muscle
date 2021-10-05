using System;
using System.Collections.Generic;
using System.IO;
using System.Text;
using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles.PythonLink.Component
{
    public class PythonInitComponent2 : GH_Component
    {

        public PythonManager pythonManager = null;

        public event GH_DocumentServer.DocumentRemovedEventHandler DocumentRemovedEvent; //does not seem to work ! 



        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public PythonInitComponent2()
          : base("Initialize PythonOld", "Python",
              "Launch Python to be able to run any calculation",
              "Muscles", "0. ToDoFirst")
        {
            DocumentRemovedEvent += DocumentClose;
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_Component.GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Anaconda3\\Scripts\\activate.bat", "ActivateConda", "Provide path to file activate.bat in Anaconda3\\Scripts directory. for instance:\n  C:\\Users\\Jferon\\Anaconda3\\Scripts\\activate.bat", GH_ParamAccess.item);
            pManager.AddBooleanParameter("Start Python", "Start", "Python/Anaconda starts and can calculate. Connect here a button or a toggle. Press button relaunches Python/Anaconda.", GH_ParamAccess.item);
            pManager[0].Optional = true;
            pManager.AddTextParameter("LogLevel", "lvl", "Level of messages in the Log file: All, Debug, Info, Warn, Error, Fatal, Off", GH_ParamAccess.item);
            pManager[2].Optional = true;

        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_Component.GH_OutputParamManager pManager)
        {

        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            List<PythonInitComponent2> PythonInitComponents = FindPythonInitComponents(this);
            if (PythonInitComponents.Count>1 && PythonInitComponents[0]!=this)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "There is already one \"Initialize Python\" Component on the Canvas.");
                return;
            }


            string ActivateCondaBat_input = "";
            bool start = false;
            string LogLvl = "Debug";
            if (!DA.GetData(0, ref ActivateCondaBat_input)) {}
            if (!DA.GetData(1, ref start)) {  }
            if (!DA.GetData(2, ref LogLvl)) { }

            LogHelper.Setup(LogLvl);


            if (start)
            {
                string activateCondaBat = @"C:\Users\Jferon\Anaconda3\Scripts\activate.bat";

                var directory = new DirectoryInfo(Directory.GetCurrentDirectory());
                string workingDirectory = null;
                if (directory.Name =="bin")
                {
                    workingDirectory = Path.Combine(directory.Parent.Parent.FullName, "MusclesPy");
                }
                else 
                {
                    workingDirectory = @"C:\Users\Jferon\OneDrive - UCL\Doctorat\recherche\code\5 - logiciel CS\Muscles\MusclesPy";
                }
                if (workingDirectory == null)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to initialize python\n Current directory is " + directory.FullName);
                    return;
                }

                PythonManager.ActivateCondaBat = activateCondaBat;
                PythonManager.WorkingDirectory = workingDirectory;
                pythonManager = PythonManager.Instance;
                AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "Anaconda is ready to perform.");
                //this.OnPingDocument().NewSolution(true); // dont do that otherwise you can't use Opossum since it is calling this method as well.
                return;
            }

            if (pythonManager != null && !start)
            {
                pythonManager.Dispose();
                pythonManager = null;
            }

            if (pythonManager==null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Anaconda stopped. Please relaunch it.");
                return;
            }
            

        }

        /// <summary>
        /// When Grasshopper is closed, kill the pythonManager
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="doc"></param>
        private void DocumentClose(GH_DocumentServer sender, GH_Document doc)
        {
            if (pythonManager != null)
            {
                pythonManager.Dispose();
            }
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
            get { return new Guid("d1e6630f-bae2-4730-8fb5-0b9dfc47bf7a"); }
        }

        public static List<PythonInitComponent2> FindPythonInitComponents(IGH_DocumentObject aComponent)
        {
            Guid PythonInitComponent_Id = new Guid("d1e6630f-bae2-4730-8fb5-0b9dfc47bf7a"); // all PythonInitComponents have this ID

            List<PythonInitComponent2> PythonInitComponents = new List<PythonInitComponent2>();

            foreach (IGH_DocumentObject obj in aComponent.OnPingDocument().Objects) //lets look at all component on the current canvas
            {
                if (obj.ComponentGuid != PythonInitComponent_Id)
                {
                    continue; //if the component is not a PythonInitComponent, skip the rest and look at the next component
                }
                PythonInitComponents.Add((PythonInitComponent2)obj); //we retrieved a PythonInitComponent on the Canvas

            }
            return PythonInitComponents;
        }

        public static bool PythonManagerFound(IGH_DocumentObject aComponent, out PythonManager pythonManager)
        {
            bool found = false;
            pythonManager = null;

            List<PythonInitComponent2> pythonInitComponents = FindPythonInitComponents(aComponent);
            List<PythonManager> ActivePythonManagers = new List<PythonManager>();

            foreach (var pythonInitComponent in pythonInitComponents)
            {
                if(pythonInitComponent.pythonManager != null)
                {
                    ActivePythonManagers.Add(pythonInitComponent.pythonManager);
                }
            }

            if(ActivePythonManagers.Count>=1) //We found at least 1 active pythonManager. (there should be only one normally). thus return it
            {
                pythonManager = ActivePythonManagers[0];
                found = true;
            }

            return found;
        }

    }
}
