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

using System;
using System.Collections;
using System.Collections.Generic;

using Rhino;
using Rhino.Geometry;

using Grasshopper;
using Grasshopper.Kernel;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;

using System.IO;
using System.Linq;
using System.Data;
using System.Drawing;
using System.Reflection;
using System.Windows.Forms;
using System.Xml;
using System.Xml.Linq;
using System.Runtime.InteropServices;

using Rhino.DocObjects;
using Rhino.Collections;
using GH_IO;
using GH_IO.Serialization;
using static Muscle.Components.GHComponentsFolders;


namespace Muscle.Components.Util
{
    public class GenesCount : GH_Component
    {
        /// <summary>
        /// Initializes a new instance of the MyComponent1 class.
        /// </summary>
        public GenesCount()
          : base("GenesCount", "GC",
              "Set the number of Genes of a Gene Pool component",
              GHAssemblyName, Folder8_Util)
        {
        }


        /// <summary>
        /// Provides an Icon for the component.
        /// </summary>
        protected override Bitmap Icon
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
            get { return new Guid("2468e7e4-8097-4022-847a-46d3eeee16fe"); }
        }

        /// <summary>
        /// Registers all the input parameters for this component.
        /// </summary>
        protected override void RegisterInputParams(GH_InputParamManager pManager)
        {
            pManager.AddTextParameter("Genes name", "Genes name", "Gene Pool component name to link with genes count", GH_ParamAccess.item);
            pManager[0].Optional = true;
            pManager.AddIntegerParameter("Count", "Count", "Number of genes in the Gene Pool component", GH_ParamAccess.item, 10);
            pManager[1].Optional = true;
        }

        /// <summary>
        /// Registers all the output parameters for this component.
        /// </summary>
        protected override void RegisterOutputParams(GH_OutputParamManager pManager)
        {
        }

        /// <summary>
        /// This is the method that actually does the work.
        /// </summary>
        /// <param name="DA">The DA object is used to retrieve from inputs and store in outputs.</param>
        protected override void SolveInstance(IGH_DataAccess DA)
        {
            // 1) Collect Inputs
            string name = null;
            int count = -1;

            if (!DA.GetData(0, ref name)) { name = "Genes"; } //default name if we can't collect a name
            if (!DA.GetData(1, ref count)) { } //default count if we can't collect a count
            Guid GenePool = new Guid("21553c44-ea62-475e-a8bb-62b2a3ee5ca5"); // all GenePool component have this ID
            foreach (IGH_DocumentObject obj in OnPingDocument().Objects) //lets look at all component on the current canvas
            {
                if (obj.ComponentGuid != GenePool)
                {
                    continue; //if the component is not a genepool, skip the rest and look at the next component
                }
                dynamic genepool = obj; //type of Genepool is: GalapagosComponents.GalapagosGeneListObject but it can't be imported with using.. No API exists to know the methods

                if (obj.NickName == name)
                {
                    if (genepool.Count == count) return;
                    genepool.Count = count;
                    //genepool.Minimum
                    //genepool.Maximum
                    //genepool.Decimals
                    //List<GH_Number> gh_values = genepool.VolatileData.FlattenData();
                    //decimal value;
                    //for (int j = 0; j < genepool.Count; j++)
                    //{
                    //    if (j < gh_values.Count)
                    //    {
                    //        value = (decimal)(gh_values[j].Value);// update the value without changing it
                    //    }
                    //    else value = Decimal.Divide(genepool.Minimum + genepool.Maximum , (decimal)2.0);

                    //    genepool.set_NormalisedValue(j, get_NormalizedValue(value, genepool));
                    //}
                    genepool.ExpirePreview(true);
                    genepool.ExpireSolution(true);
                }
                //Helper Functions

            }


        }
        private decimal get_NormalizedValue(decimal unnormalized, dynamic genepool)
        {
            return (unnormalized - genepool.Minimum) / (genepool.Maximum - genepool.Minimum);
        }

        private decimal get_UnnormalizedValue(decimal normalized, dynamic genepool)
        {
            return Math.Round(genepool.Minimum + (genepool.Maximum - genepool.Minimum) * normalized, genepool.Decimals);
        }

    }
}

