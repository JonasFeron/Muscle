﻿// Muscle

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

using GH_IO.Serialization;
using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;

namespace Muscle.View
{
    public class GH_CrossSection : GH_Goo<ICrossSection>
    {

        #region Properties

        public override bool IsValid { get { return Value.IsValid; } }

        public override string IsValidWhyNot
        {
            get
            {
                if (Value.Dimension <= 0) { return "Dimension is less than or equal to 0.0cm"; }
                if (Value.Thickness <= 0) { return "Thickness is less than or equal to 0.0cm"; }
                if (Value.Thickness > Value.Dimension / 2.0) { return "Thickness is greater than physically possible."; }

                return string.Empty;
            }
        }

        public override string TypeDescription { get { return "Cross section of a structural element."; } }
        public override string TypeName { get { return Value.ShapeName; } }

        public override ICrossSection Value { get => base.Value; set => base.Value = value; }

        #endregion Properties

        #region Constructors

        public GH_CrossSection()
        {
            Value = new CS_Circular();
        }

        public GH_CrossSection(ICrossSection cs) : base(cs)
        {
            Value = cs;
        }

        public GH_CrossSection(GH_Goo<ICrossSection> other) : base(other)
        {
            Value = other.Value;
        }

        #endregion Constructors

        #region Methods

        public override bool CastFrom(object source)
        {
            if (source is ICrossSection)
            {
                ICrossSection cs = source as ICrossSection;
                Value = cs;
                return true;
            }
            // Handle the case when an ICrossSection is wrapped in a GH_ObjectWrapper
            if (source is GH_ObjectWrapper wrapper && wrapper.Value is ICrossSection)
            {
                Value = (ICrossSection)wrapper.Value;
                return true;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(ref Q target)
        {
            if (typeof(Q).IsAssignableFrom(typeof(ICrossSection)))
            {
                object cs = Value;
                target = (Q)cs;
                return true;
            }

            target = default;

            return false;
        }

        public override IGH_Goo Duplicate()
        {
            return new GH_CrossSection(this);
        }

        //public override bool Read(GH_IReader reader) //used in Cross Section Parameter
        //{
        //    string TypeName = reader.GetString("type name");

        //    if (TypeName == "Circle cross section")
        //    {
        //        double diameter = reader.Getdouble("dimension");
        //        double thickness = reader.Getdouble("thickness");
        //        Value = new CS_Circular(diameter, thickness);
        //    }
        //    else if (TypeName == "Square cross section")
        //    {
        //        double diameter = reader.Getdouble("dimension");
        //        double thickness = reader.Getdouble("thickness");
        //        Value = new CS_Square(diameter, thickness);
        //    }
        //    else { return false; }

        //    return base.Read(reader);
        //}

        public override object ScriptVariable()
        {
            return Duplicate();
        }

        public override string ToString()
        {
            return Value.ToString();
        }
        //public override bool Write(GH_IWriter writer)
        //{
        //    writer.SetString("type name", Value.ShapeName);
        //    writer.Setdouble("dimension", Value.Dimension);
        //    writer.Setdouble("thickness", Value.Thickness);


        //    return base.Write(writer);
        //}

        #endregion Methods

    }
}
