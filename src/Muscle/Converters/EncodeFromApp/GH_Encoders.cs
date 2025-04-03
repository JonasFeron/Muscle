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
    public static class GH_Encoders
    {
        #region Number Conversion
        public static GH_Structure<GH_Number> ToTree(double[,] array)
        {
            GH_Structure<GH_Number> tree = new GH_Structure<GH_Number>();
            int rows = array.GetLength(0);
            int cols = array.GetLength(1);

            for (int i = 0; i < rows; i++)
            {
                GH_Path path = new GH_Path(i);
                List<GH_Number> branch = new List<GH_Number>(cols);
                for (int j = 0; j < cols; j++)
                {
                    branch.Add(new GH_Number(array[i, j]));
                }
                tree.AppendRange(branch, path);
            }
            return tree;
        }

        public static List<GH_Number> ToBranch(double[] array)
        {
            return array.Select(n => new GH_Number(n)).ToList();
        }

        public static GH_Structure<GH_Number> ToTree(double[] array)
        {
            GH_Structure<GH_Number> tree = new GH_Structure<GH_Number>();
            GH_Path path = new GH_Path(0);
            List<GH_Number> branch = new List<GH_Number>(array.Length);
            
            for (int i = 0; i < array.Length; i++)
            {
                branch.Add(new GH_Number(array[i]));
            }
            
            tree.AppendRange(branch, path);
            return tree;
        }
        #endregion Number Conversion

        #region Vector3d Conversion
        public static GH_Structure<GH_Vector> ToTree(Vector3d[,] array)
        {
            GH_Structure<GH_Vector> tree = new GH_Structure<GH_Vector>();
            int rows = array.GetLength(0);
            int cols = array.GetLength(1);

            for (int i = 0; i < rows; i++)
            {
                GH_Path path = new GH_Path(i);
                List<GH_Vector> branch = new List<GH_Vector>(cols);
                for (int j = 0; j < cols; j++)
                {
                    branch.Add(new GH_Vector(array[i, j]));
                }
                tree.AppendRange(branch, path);
            }
            return tree;
        }

        public static List<GH_Vector> ToBranch(Vector3d[] array)
        {
            return array.Select(n => new GH_Vector(n)).ToList();
        }

        #endregion Vector3d Conversion

        #region Point3d Conversion
        public static GH_Structure<GH_Point> ToTree(Point3d[,] array)
        {
            GH_Structure<GH_Point> tree = new GH_Structure<GH_Point>();
            int rows = array.GetLength(0);
            int cols = array.GetLength(1);

            for (int i = 0; i < rows; i++)
            {
                GH_Path path = new GH_Path(i);
                List<GH_Point> branch = new List<GH_Point>(cols);
                for (int j = 0; j < cols; j++)
                {
                    branch.Add(new GH_Point(array[i, j]));
                }
                tree.AppendRange(branch, path);
            }
            return tree;
        }


        public static List<GH_Point> ToBranch(Point3d[] array)
        {
            return array.Select(n => new GH_Point(n)).ToList();
        }
        #endregion Point3d Conversion

        #region Prestress Conversion
        public static List<GH_Prestress> ToBranch(List<Prestress> prestresses)
        {
            return prestresses.Select(p => new GH_Prestress(p)).ToList();
        }
        #endregion Prestress Conversion
    }
}
