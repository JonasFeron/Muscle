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

using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;
using Rhino.Geometry;
using Grasshopper.Kernel;
using System;
using System.Drawing;

namespace Muscle.View
{
    public class GH_Prestress : GH_GeometricGoo<Prestress>, IGH_PreviewData
    {
        #region Properties

        private static readonly Color prestressColor = Color.Orange;
        
        public BoundingBox ClippingBox { get { return Boundingbox; } }

        public override BoundingBox Boundingbox
        {
            get
            {
                if (Value == null || !Value.IsValid) return BoundingBox.Empty;
                
                BoundingBox box = Value.Element.Line.BoundingBox;
                
                // Expand the bounding box to include the visualization of the forces
                double amplification = MuscleConfig.DisplayPrestressAmpli / 10000.0;
                Vector3d force0 = Value.Element.Line.UnitTangent * Value.EquivalentTension * amplification;
                Vector3d force1 = -Value.Element.Line.UnitTangent * Value.EquivalentTension * amplification;
                
                box.Union(new BoundingBox(new Point3d[] { 
                    Value.Element.Line.From, 
                    Value.Element.Line.From + force0,
                    Value.Element.Line.To,
                    Value.Element.Line.To + force1
                }));
                
                return box;
            }
        }

        public override Prestress Value { set; get; }
        public override bool IsValid { get { return Value.IsValid; } }

        public override string TypeDescription { get { return "Initial force in the element considering that all nodes are fixed in space."; } }

        public override string TypeName { get { return "Prestress"; } }

        #endregion Properties

        #region Constructors

        public GH_Prestress() : base()
        {
            Value = new Prestress();
        }

        public GH_Prestress(Prestress prestress) : base(prestress)
        {
            Value = prestress;
        }

        public GH_Prestress(GH_Goo<Prestress> gh_prestress)
        {
            Value = gh_prestress.Value.Duplicate();
        }
        
        public override IGH_Goo Duplicate()
        {
            return new GH_Prestress(this);
        }

        #endregion Constructors


        #region Methods

        public override bool CastFrom(object source)
        {
            if (source == null) { return false; }

            if (source is Prestress)
            {
                Value = (Prestress)source;
                return true;
            }
            // Handle the case when a Prestress is wrapped in a GH_ObjectWrapper
            if (source is GH_ObjectWrapper wrapper && wrapper.Value is Prestress)
            {
                Value = (Prestress)wrapper.Value;
                return true;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(ref Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(Prestress)))
            {
                object initialforce = Value;
                target = (Q)initialforce;
                return true;
            }
            if (typeof(Q).IsAssignableFrom(typeof(double)))
            {
                object force = Value.FreeLengthVariation;
                target = (Q)force;
                return true;
            }

            if (typeof(Q).IsAssignableFrom(typeof(Element)))
            {
                object e = Value.Element;
                target = (Q)e;
                return true;
            }

            target = default;

            return false;
        }

        public void DrawViewportMeshes(GH_PreviewMeshArgs args)
        {
            if (Value == null || !Value.IsValid) return;
            
            double displayAmpli = MuscleConfig.DisplayPrestressAmpli;
            
            // Force at start point (From)
            PointLoad load0 = Value.EquivalentPointLoad0;
            Vector3d v_display0 = load0.Vector * displayAmpli / 10000.0;
            
            // Force at end point (To)
            PointLoad load1 = Value.EquivalentPointLoad1;
            Vector3d v_display1 = load1.Vector * displayAmpli / 10000.0;
            
            // Draw cones for each component of the forces
            DrawForceComponentCones(args, load0.Point, v_display0);
            DrawForceComponentCones(args, load1.Point, v_display1);
        }
        
        private void DrawForceComponentCones(GH_PreviewMeshArgs args, Point3d point, Vector3d force)
        {
            if (force.Length < 0.001) return;
            
            // Draw a single cone in the direction of the force vector
            double height = force.Length/4;
            double radius = height / 2.5;
            
            // Create a plane aligned with the force vector
            Vector3d direction = -force;
            direction.Unitize();
            
            Plane conePlane = new Plane(point+force, direction);
            args.Pipeline.DrawCone(new Cone(conePlane, height, radius), prestressColor);
        }

        public void DrawViewportWires(GH_PreviewWireArgs args)
        {
            if (Value == null || !Value.IsValid) return;
            
            double displayAmpli = MuscleConfig.DisplayPrestressAmpli;
            int _decimal = MuscleConfig.DisplayDecimals;
            
            // Get camera information for text display
            Plane plane;
            args.Viewport.GetCameraFrame(out plane);
            
            // Draw the element line
            // args.Pipeline.DrawLine(Value.Element.Line, Color.Gray, 1);
            
            // Force at start point (From)
            PointLoad load0 = Value.EquivalentPointLoad0;
            Vector3d v_display0 = load0.Vector * displayAmpli / 10000.0;
            
            // Force at end point (To)
            PointLoad load1 = Value.EquivalentPointLoad1;
            Vector3d v_display1 = load1.Vector * displayAmpli / 10000.0;
            
            // Draw force vectors and labels
            double freeLengthVariation = Value.FreeLengthVariation; // (m)
            DrawForceVectors(args, load0.Point, v_display0, freeLengthVariation, _decimal, false);
            DrawForceVectors(args, load1.Point, v_display1, freeLengthVariation, _decimal, true); // show text "free length variation = x mm" at only one end
        }
        
        private void DrawForceVectors(GH_PreviewWireArgs args, Point3d point, Vector3d force, double freeLengthVariation, int decimals, bool showText)
        {
            double pixelsPerUnit;
            args.Viewport.GetWorldToScreenScale(point, out pixelsPerUnit);
            
            Plane textPlane;
            args.Viewport.GetCameraFrame(out textPlane);
            
            string lengtheningText = string.Format("{0} mm", Math.Round(freeLengthVariation * 1000, decimals, MidpointRounding.AwayFromZero));
            
            // Draw the force as a single vector
            if (force.Length > 0)
            {
                Point3d start = point;
                args.Pipeline.DrawLine(new Line(start, force), prestressColor, 2);
                
                // Position text at the end of the vector
                textPlane.Origin = start + force;
                if (showText)
                {
                    args.Pipeline.Draw3dText(lengtheningText, prestressColor, textPlane, 14 / pixelsPerUnit, "Lucida Console");
                }
            }
        }

        public override IGH_GeometricGoo DuplicateGeometry()
        {
            return new GH_Prestress(this);
        }

        public override BoundingBox GetBoundingBox(Transform xform)
        {
            return xform.TransformBoundingBox(Boundingbox);
        }

        public override IGH_GeometricGoo Morph(SpaceMorph xmorph)
        {
            if (Value == null || !Value.IsValid) return null;
            
            // Create a new prestress with morphed element
            GH_Prestress result = new GH_Prestress(this);
            
            // We would need to morph the element, but this might require deeper changes
            // For now, we'll just return a duplicate
            return result;
        }

        public override IGH_GeometricGoo Transform(Transform xform)
        {
            if (Value == null || !Value.IsValid) return null;
            
            // Create a new prestress with transformed element
            GH_Prestress result = new GH_Prestress(this);
            
            // Note: This is a simplified transformation that doesn't fully transform the element
            // A more complete implementation would transform the element's line and other properties
            return result;
        }

        public override object ScriptVariable()
        {
            return Value;
        }

        public override string ToString()
        {
            return Value.ToString();
        }
        #endregion Methods

    }
}