using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Text;
using Grasshopper.Kernel;
using Rhino.Geometry;

namespace Muscles.PythonLink.Component
{
    public class PythonInitComponent : GH_Component
    {

        public event GH_DocumentServer.DocumentRemovedEventHandler DocumentRemovedEvent; //does not seem to work ! 



        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public PythonInitComponent()
          : base("Initialize Python", "Python",
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
            pManager.AddBooleanParameter("User mode", "user", "true for user mode, false for developer mode.", GH_ParamAccess.item,true); 
            pManager[0].Optional = true;
            pManager.AddBooleanParameter("Start Python", "Start", "Connect here a toggle. If true, Python/Anaconda starts and can calculate.", GH_ParamAccess.item);

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
            bool user_mode = true;
            bool start = false;
            string LogLvl = "Debug";
            if (!DA.GetData(0, ref user_mode)) {}
            if (!DA.GetData(1, ref start)) {  }
            if (!DA.GetData(2, ref LogLvl)) { }

            LogHelper.Setup(LogLvl);
            AccessToAll.user_mode = user_mode;

            if (start && AccessToAll.pythonManager != null)
            {
                AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "There is already one Anaconda ready to perform on the Canvas.");
                return;
            }

            if (start && AccessToAll.pythonManager == null)
            {
                string activateCondaBat = null;
                string workingDirectory = null;
                
                if (user_mode)
                {
                    DirectoryInfo librairies = SpecialFolder();
                    string Folder_Muscles = Path.Combine(librairies.FullName, AccessToAll.assemblyTitle);
                    AccessToAll.Main_Folder = Folder_Muscles;
                    //retrieve path to anaconda
                    activateCondaBat = PathToAnaconda(Folder_Muscles);

                    //define path to MusclesPy
                    workingDirectory = Path.Combine(AccessToAll.Main_Folder, "MusclesPy");

                }
                else // in case of working in debug/developer mode
                {
                    activateCondaBat = @"C:\Users\jferon\Anaconda3\Scripts\activate.bat";

                    var directory = new DirectoryInfo(Directory.GetCurrentDirectory()); // return bin folder
                    AccessToAll.Main_Folder = directory.Parent.Parent.FullName;
                    workingDirectory = Path.Combine(AccessToAll.Main_Folder, "MusclesPy");   //  @"C:\Users\Jferon\OneDrive - UCL\Doctorat\recherche\code\5 - logiciel CS\Muscles\MusclesPy";
                }
                if (workingDirectory == null)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to retrieve python scripts\n Check your path \\AppData\\Roaming\\Grasshopper\\Libraries\\Muscles vx.x\\MusclesPy");
                    return;
                }
                if (activateCondaBat == null)
                {
                    AddRuntimeMessage(GH_RuntimeMessageLevel.Error, "Failed to retrieve Anaconda script: activate.bat\n Check that PathToAnaconda is well configured in \\AppData\\Roaming\\Grasshopper\\Libraries\\Muscles vx.x\\PathToAnaconda.txt");
                    return;
                }



                PythonManager.ActivateCondaBat = activateCondaBat;
                PythonManager.WorkingDirectory = workingDirectory;
                AccessToAll.pythonManager = PythonManager.Instance;
                AddRuntimeMessage(GH_RuntimeMessageLevel.Remark, "Anaconda is ready to perform.");
                //this.OnPingDocument().NewSolution(true); // dont do that otherwise you can't use Opossum since it is calling this method as well.
                return;
            }

            if (!start && AccessToAll.pythonManager != null )
            {
                AccessToAll.pythonManager.Dispose();
                AccessToAll.pythonManager = null;
            }

            if (AccessToAll.pythonManager ==null)
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
            if (AccessToAll.pythonManager != null)
            {
                AccessToAll.pythonManager.Dispose();
                AccessToAll.pythonManager = null;
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
            get { return new Guid("ee9c0d81-1f1e-4279-9421-a286949a869b"); }
        }

        /// <summary>
        /// return the directory with path : "C:\\Users\\Jferon\\AppData\\Roaming\\Grasshopper\\Libraries\\"
        /// </summary>
        /// <returns></returns>
        private DirectoryInfo SpecialFolder()
        {
            List<GH_AssemblyFolderInfo> assemblyFolders = Grasshopper.Folders.AssemblyFolders;
            foreach(GH_AssemblyFolderInfo dir in assemblyFolders)
            {
                if (dir.Folder.Contains("\\AppData\\Roaming\\Grasshopper\\Libraries"))
                {
                    return new DirectoryInfo(dir.Folder);
                }
            }
            return null;
        }
        private string PathToAnaconda(string Folder_Muscles)
        {
            string file = "PathToAnaconda.txt";
            try
            {
                string full_path_to_file = Path.Combine(Folder_Muscles, file);
                string[] lines = System.IO.File.ReadAllLines(full_path_to_file);
                foreach (var line in lines)
                {
                    if (line.Contains("Users\\Jferon"))
                    {
                        AddRuntimeMessage(GH_RuntimeMessageLevel.Warning, "Please configure the path to anaconda in your special folder: \\AppData\\Roaming\\Grasshopper\\Libraries\\Muscles vx.x\\PathToAnaconda.txt");
                    }
                    if (line.Contains("activate.bat")|| line.Contains("activate"))
                    {
                        return line;
                    }
                }
                return null;

            }
            catch
            {
                return null;
            }
        }



    //public static List<PythonInitComponent> FindPythonInitComponents(IGH_DocumentObject aComponent)
    //{
    //    Guid PythonInitComponent_Id = new Guid("d1e6630f-bae2-4730-8fb5-0b9dfc47bf7a"); // all PythonInitComponents have this ID

    //    List<PythonInitComponent> PythonInitComponents = new List<PythonInitComponent>();

    //    foreach (IGH_DocumentObject obj in aComponent.OnPingDocument().Objects) //lets look at all component on the current canvas
    //    {
    //        if (obj.ComponentGuid != PythonInitComponent_Id)
    //        {
    //            continue; //if the component is not a PythonInitComponent, skip the rest and look at the next component
    //        }
    //        PythonInitComponents.Add((PythonInitComponent)obj); //we retrieved a PythonInitComponent on the Canvas

    //    }
    //    return PythonInitComponents;
    //}

    //public static bool PythonManagerFound(IGH_DocumentObject aComponent, out PythonManager pythonManager)
    //{
    //    bool found = false;
    //    pythonManager = null;

    //    List<PythonInitComponent> pythonInitComponents = FindPythonInitComponents(aComponent);
    //    List<PythonManager> ActivePythonManagers = new List<PythonManager>();

    //    foreach (var pythonInitComponent in pythonInitComponents)
    //    {
    //        if(pythonInitComponent.pythonManager != null)
    //        {
    //            ActivePythonManagers.Add(pythonInitComponent.pythonManager);
    //        }
    //    }

    //    if(ActivePythonManagers.Count>=1) //We found at least 1 active pythonManager. (there should be only one normally). thus return it
    //    {
    //        pythonManager = ActivePythonManagers[0];
    //        found = true;
    //    }

    //    return found;
    //}

}
}
