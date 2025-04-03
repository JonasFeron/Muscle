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
using System.Collections.Generic;
using System.Linq;
using Grasshopper.Kernel.Types;
using Grasshopper.Kernel.Data;
using Rhino.Geometry;
using MuscleApp.ViewModel;
using Muscle.View;

namespace Muscle.Converters
{
    /// <summary>
    /// Provides methods to convert Grasshopper data types to MuscleApp ViewModel types.
    /// This ensures MuscleApp remains independent from Grasshopper and Muscle.
    /// </summary>
    public static class GH_Decoders
    {

        #region Number Conversion
        public static double[] ToArray(List<GH_Number> branch)
        {
            return branch.Select(n => n.Value).ToArray();
        }

        /// <summary>
        /// Converts a GH_Structure of GH_Number to a 2D double array.
        /// Each branch in the data tree becomes a row in the resulting array.
        /// </summary>
        /// <param name="dataTree">The Grasshopper data tree to convert</param>
        /// <returns>A 2D array where each row corresponds to a branch in the data tree</returns>
        public static double[,] To2dArray(GH_Structure<GH_Number> dataTree)
        {
            if (dataTree == null || dataTree.DataCount == 0)
                return new double[0, 0];

            // Get all branches
            var branches = dataTree.Branches;
            int rows = branches.Count;
            
            // Determine the number of columns (use the longest branch)
            int cols = branches.Max(branch => branch.Count);
            
            // Create the 2D array
            double[,] result = new double[rows, cols];
            
            // Fill the array
            for (int i = 0; i < rows; i++)
            {
                var branch = branches[i];
                for (int j = 0; j < branch.Count; j++)
                {
                    result[i, j] = branch[j].Value;
                }
                
                // If a branch is shorter than the longest branch, the remaining values stay as 0
            }
            
            return result;
        }
        #endregion Number Conversion

        #region Support Conversion

        /// <summary>
        /// Converts a GH_Support to a MuscleApp.ViewModel.Support
        /// </summary>
        /// <param name="ghSupport">The Grasshopper support to convert</param>
        /// <returns>A MuscleApp.ViewModel.Support</returns>
        public static Support ToSupport(GH_Support ghSupport)
        {
            return ghSupport.Value;
        }

        /// <summary>
        /// Converts a list of GH_Support objects to a list of MuscleApp.ViewModel.Support objects
        /// </summary>
        /// <param name="ghSupports">The list of Grasshopper supports to convert</param>
        /// <returns>A list of MuscleApp.ViewModel.Support objects</returns>
        public static List<Support> ToSupportList(List<GH_Support> ghSupports)
        {
            return ghSupports.Select(s => s.Value).ToList();
        }

        /// <summary>
        /// Extracts Support objects from a Grasshopper data tree
        /// </summary>
        /// <param name="tree">The Grasshopper data tree containing supports</param>
        /// <returns>A list of MuscleApp.ViewModel.Support objects</returns>
        public static List<Support> ToSupportList(GH_Structure<IGH_Goo> tree)
        {
            return FromTree<Support, GH_Support>(tree);
        }
        #endregion Support Conversion

        #region Element Conversion

        /// <summary>
        /// Converts a GH_Element to a MuscleApp.ViewModel.Element
        /// </summary>
        /// <param name="ghElement">The Grasshopper element to convert</param>
        /// <returns>A MuscleApp.ViewModel.Element instance</returns>
        public static Element ToElement(GH_Element ghElement)
        {
            return ghElement.Value;
        }

        /// <summary>
        /// Converts a collection of GH_Element objects to a list of MuscleApp.ViewModel.Element objects
        /// </summary>
        /// <param name="ghElements">The collection of Grasshopper elements to convert</param>
        /// <returns>A list of MuscleApp.ViewModel.Element instances</returns>
        public static List<Element> ToElementList(List<GH_Element> ghElements)
        {
            return ghElements.Select(e => e.Value).ToList();
        }

        /// <summary>
        /// Extracts Element objects from a Grasshopper data tree
        /// </summary>
        /// <param name="tree">The Grasshopper data tree containing elements</param>
        /// <returns>A list of MuscleApp.ViewModel.Element objects</returns>
        public static List<Element> ToElementList(GH_Structure<IGH_Goo> tree)
        {
            return FromTree<Element, GH_Element>(tree);
        }

        #endregion Element Conversion

        #region Point Conversion

        /// <summary>
        /// Converts a GH_Point to a Rhino.Geometry.Point3d
        /// </summary>
        /// <param name="ghPoint">The Grasshopper point to convert</param>
        /// <returns>A Point3d instance</returns>
        public static Point3d ToPoint3d(GH_Point ghPoint)
        {
            if (ghPoint == null || !ghPoint.IsValid)
                return Point3d.Unset;

            return ghPoint.Value;
        }


        /// <summary>
        /// Extracts Point3d objects from a Grasshopper data tree
        /// </summary>
        /// <param name="tree">The Grasshopper data tree containing points</param>
        /// <returns>A list of Point3d instances</returns>
        public static List<Point3d> ToPoint3dList(GH_Structure<GH_Point> ghPoints)
        {   
            return ghPoints.FlattenData().Select(ghp => ghp.Value).ToList();
        }

        #endregion Point Conversion

        #region PointLoad Conversion
        /// <summary>
        /// Converts a GH_PointLoad to a MuscleApp.ViewModel.PointLoad
        /// </summary>
        /// <param name="ghPointLoad">The Grasshopper point load to convert</param>
        /// <returns>A MuscleApp.ViewModel.PointLoad</returns>
        public static PointLoad ToPointLoad(GH_PointLoad ghPointLoad)
        {
            return ghPointLoad.Value;
        }

        /// <summary>
        /// Converts a list of GH_PointLoad objects to a list of MuscleApp.ViewModel.PointLoad objects
        /// </summary>
        /// <param name="ghPointLoads">The list of Grasshopper point loads to convert</param>
        /// <returns>A list of MuscleApp.ViewModel.PointLoad objects</returns>
        public static List<PointLoad> ToPointLoadList(List<GH_PointLoad> ghPointLoads)
        {
            return ghPointLoads.Select(pl => pl.Value).ToList();
        }

        /// <summary>
        /// Extracts PointLoad objects from a Grasshopper data tree
        /// </summary>
        /// <param name="tree">The Grasshopper data tree containing point loads</param>
        /// <returns>A list of MuscleApp.ViewModel.PointLoad objects</returns>
        public static List<PointLoad> ToPointLoadList(GH_Structure<IGH_Goo> tree)
        {
            return FromTree<PointLoad, GH_PointLoad>(tree);
        }
        #endregion PointLoad Conversion

        #region Prestress Conversion
        /// <summary>
        /// Converts a GH_Prestress to a MuscleApp.ViewModel.Prestress
        /// </summary>
        /// <param name="ghPrestress">The Grasshopper prestress to convert</param>
        /// <returns>A MuscleApp.ViewModel.Prestress</returns>
        public static Prestress ToPrestress(GH_Prestress ghPrestress)
        {
            return ghPrestress.Value;
        }

        /// <summary>
        /// Converts a list of GH_Prestress objects to a list of MuscleApp.ViewModel.Prestress objects
        /// </summary>
        /// <param name="ghPrestresses">The list of Grasshopper prestresses to convert</param>
        /// <returns>A list of MuscleApp.ViewModel.Prestress objects</returns>
        public static List<Prestress> ToPrestressList(List<GH_Prestress> ghPrestresses)
        {
            return ghPrestresses.Select(ps => ps.Value).ToList();
        }

        /// <summary>
        /// Extracts Prestress objects from a Grasshopper data tree
        /// </summary>
        /// <param name="tree">The Grasshopper data tree containing prestresses</param>
        /// <returns>A list of MuscleApp.ViewModel.Prestress objects</returns>
        public static List<Prestress> ToPrestressList(GH_Structure<IGH_Goo> tree)
        {
            return FromTree<Prestress, GH_Prestress>(tree);
        }
        #endregion Prestress Conversion

        #region Double Conversion
        /// <summary>
        /// Converts a list of GH_Number objects to a list of double values
        /// </summary>
        /// <param name="ghNumbers">The list of Grasshopper numbers to convert</param>
        /// <returns>A list of double values</returns>
        public static List<double> ToDoubleList(List<GH_Number> ghNumbers)
        {
            return ghNumbers.Select(n => n.Value).ToList();
        }

        /// <summary>
        /// Extracts double values from a Grasshopper data tree
        /// </summary>
        /// <param name="tree">The Grasshopper data tree containing numbers</param>
        /// <returns>A list of double values</returns>
        public static List<double> ToDoubleList(GH_Structure<GH_Number> tree)
        {
            List<double> result = new List<double>();
            
            foreach (var branch in tree.Branches)
            {
                result.AddRange(branch.Select(n => n.Value));
            }
            
            return result;
        }

        /// <summary>
        /// Extracts double values from a Grasshopper data tree with IGH_Goo items
        /// </summary>
        /// <param name="tree">The Grasshopper data tree containing numbers</param>
        /// <returns>A list of double values</returns>
        public static List<double> ToDoubleList(GH_Structure<IGH_Goo> tree)
        {
            List<double> result = new List<double>();
            
            foreach (var branch in tree.Branches)
            {
                foreach (var item in branch)
                {
                    if (item is GH_Number ghNumber)
                    {
                        result.Add(ghNumber.Value);
                    }
                }
            }
            
            return result;
        }
        #endregion Double Conversion

        #region Generic Conversion Methods
        /// <summary>
        /// Generic method to extract objects of type T from a Grasshopper data tree containing objects of type TGH
        /// </summary>
        /// <typeparam name="T">The target type (e.g., PointLoad, Prestress)</typeparam>
        /// <typeparam name="GH_T">The Grasshopper wrapper type (e.g., GH_PointLoad, GH_Prestress)</typeparam>
        /// <param name="tree">The Grasshopper data tree</param>
        /// <returns>A list of objects of type T</returns>
        public static List<T> FromTree<T, GH_T>(GH_Structure<IGH_Goo> tree) where GH_T : GH_Goo<T>
        {
            List<T> result = new List<T>();
            
            foreach (var branch in tree.Branches)
            {
                result.AddRange(FromBranch<T, GH_T>(branch));
            }
            
            return result;
        }

        /// <summary>
        /// Generic method to extract objects of type T from a Grasshopper branch containing objects of type TGH
        /// </summary>
        /// <typeparam name="T">The target type (e.g., PointLoad, Prestress)</typeparam>
        /// <typeparam name="GH_T">The Grasshopper wrapper type (e.g., GH_PointLoad, GH_Prestress)</typeparam>
        /// <param name="branch">The Grasshopper branch</param>
        /// <returns>A list of objects of type T</returns>
        public static List<T> FromBranch<T, GH_T>(List<IGH_Goo> branch) where GH_T : GH_Goo<T>
        {
            List<T> result = new List<T>();
            
            foreach (var item in branch)
            {
                if (item is GH_T ghItem)
                {
                    result.Add(ghItem.Value);
                }
            }
            
            return result;
        }
        #endregion Generic Conversion Methods
    }
}
