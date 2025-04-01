// Muscle

// Copyright <2015-2025> <Université catholique de Louvain (UCLouvain)>

// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at

//     http://www.apache.org/licenses/LICENSE-2.0

// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

// List of the contributors to the development of Muscle: see NOTICE file.
// Description and complete License: see NOTICE file.
// ------------------------------------------------------------------------------------------------------------

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
//------------------------------------------------------------------------------------------------------------

//this file was imported from the official Grasshopper Template:
//https://github.com/mcneel/RhinoVisualStudioExtensions/releases
//and is used quasi without modification.
//------------------------------------------------------------------------------------------------------------
using System;
using System.Drawing;
using Grasshopper;
using Grasshopper.Kernel;

namespace Muscle
{
    public class MuscleInfo : GH_AssemblyInfo
    {
        public override string Name => "Muscle";

        //Return a 24x24 pixel bitmap to represent this GHA library.
        public override Bitmap Icon => null;

        //Return a short string describing the purpose of this GHA library.
        public override string Description => "Muscle for Grasshopper is devoted to the design, the analysis and the optimization of tensegrity, tension-based and truss-like structures with element forces only in tension (muscles) or in compression (bones).";

        public override Guid Id => new Guid("f8029d34-993d-4dcb-bf79-9afcd328578d");

        //Return a string identifying you or your company.
        public override string AuthorName => "Jonas FERON - Université catholique de Louvain (UCLouvain)";

        //Return a string representing your preferred contact details.
        public override string AuthorContact => "";

        //Return a string representing the version.  This returns the same version as the assembly.
        public override string AssemblyVersion => GetType().Assembly.GetName().Version.ToString();
    }
}