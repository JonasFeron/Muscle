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
        #region Support Conversion

        /// <summary>
        /// Converts a GH_Support to a MuscleApp.ViewModel.Support
        /// </summary>
        /// <param name="ghSupport">The Grasshopper support to convert</param>
        /// <returns>A MuscleApp.ViewModel.Support instance</returns>
        public static Support ToSupport(GH_Support ghSupport)
        {
            if (ghSupport == null || !ghSupport.IsValid)
                return null;

            return ghSupport.Value;
        }

        /// <summary>
        /// Converts a collection of GH_Support objects to a list of MuscleApp.ViewModel.Support objects
        /// </summary>
        /// <param name="ghSupports">The collection of Grasshopper supports to convert</param>
        /// <returns>A list of MuscleApp.ViewModel.Support instances</returns>
        public static List<Support> ToSupports(IEnumerable<GH_Support> ghSupports)
        {
            if (ghSupports == null)
                return new List<Support>();

            return ghSupports
                .Where(s => s != null && s.IsValid)
                .Select(s => s.Value)
                .ToList();
        }

        /// <summary>
        /// Extracts Support objects from a Grasshopper data tree
        /// </summary>
        /// <param name="ghSupportsTree">Grasshopper data tree containing support objects</param>
        /// <returns>A list of MuscleApp.ViewModel.Support instances</returns>
        public static List<Support> ToSupports(GH_Structure<IGH_Goo> ghSupportsTree)
        {
            if (ghSupportsTree == null)
                return new List<Support>();

            List<Support> supports = new List<Support>();
            
            foreach (var path in ghSupportsTree.Paths)
            {
                var branch = ghSupportsTree[path];
                foreach (var goo in branch)
                {
                    if (goo is GH_Support ghSupport && ghSupport.IsValid)
                    {
                        supports.Add(ghSupport.Value);
                    }
                }
            }
            
            return supports;
        }

        #endregion

        #region Element Conversion

        /// <summary>
        /// Converts a GH_Element to a MuscleApp.ViewModel.Element
        /// </summary>
        /// <param name="ghElement">The Grasshopper element to convert</param>
        /// <returns>A MuscleApp.ViewModel.Element instance</returns>
        public static Element ToElement(GH_Element ghElement)
        {
            if (ghElement == null || !ghElement.IsValid)
                return null;

            return ghElement.Value;
        }

        /// <summary>
        /// Converts a collection of GH_Element objects to a list of MuscleApp.ViewModel.Element objects
        /// </summary>
        /// <param name="ghElements">The collection of Grasshopper elements to convert</param>
        /// <returns>A list of MuscleApp.ViewModel.Element instances</returns>
        public static List<Element> ToElements(IEnumerable<GH_Element> ghElements)
        {
            if (ghElements == null)
                return new List<Element>();

            return ghElements
                .Where(e => e != null && e.IsValid)
                .Select(e => e.Value)
                .ToList();
        }

        /// <summary>
        /// Extracts Element objects from a Grasshopper data tree
        /// </summary>
        /// <param name="ghElementsTree">Grasshopper data tree containing element objects</param>
        /// <returns>A list of MuscleApp.ViewModel.Element instances</returns>
        public static List<Element> ToElements(GH_Structure<IGH_Goo> ghElementsTree)
        {
            if (ghElementsTree == null)
                return new List<Element>();

            List<Element> elements = new List<Element>();
            
            foreach (var path in ghElementsTree.Paths)
            {
                var branch = ghElementsTree[path];
                foreach (var goo in branch)
                {
                    if (goo is GH_Element ghElement && ghElement.IsValid)
                    {
                        elements.Add(ghElement.Value);
                    }
                }
            }
            
            return elements;
        }

        #endregion

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
        /// Converts a collection of GH_Point objects to a list of Point3d objects
        /// </summary>
        /// <param name="ghPoints">The collection of Grasshopper points to convert</param>
        /// <returns>A list of Point3d instances</returns>
        public static List<Point3d> ToPoint3ds(IEnumerable<GH_Point> ghPoints)
        {
            if (ghPoints == null)
                return new List<Point3d>();

            return ghPoints
                .Where(p => p != null && p.IsValid)
                .Select(p => p.Value)
                .ToList();
        }

        /// <summary>
        /// Extracts Point3d objects from a Grasshopper data tree
        /// </summary>
        /// <param name="ghPointsTree">Grasshopper data tree containing point objects</param>
        /// <returns>A list of Point3d instances</returns>
        public static List<Point3d> ToPoint3ds(GH_Structure<GH_Point> ghPointsTree)
        {
            if (ghPointsTree == null)
                return new List<Point3d>();

            List<Point3d> points = new List<Point3d>();
            
            foreach (var path in ghPointsTree.Paths)
            {
                var branch = ghPointsTree[path];
                foreach (var ghPoint in branch)
                {
                    if (ghPoint != null && ghPoint.IsValid)
                    {
                        points.Add(ghPoint.Value);
                    }
                }
            }
            
            return points;
        }

        #endregion
    }
}
