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
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using MuscleApp.ViewModel;
using Rhino.Geometry;


namespace Muscle.View
{

    public class GH_Truss : GH_Goo<Truss>
    {
        // All data used in Grasshopper must implement the IGH_Goo interface. 
        // IGH_Goo defines the bare minimum of methods and properties for any kind of data before it is allowed to play ball
        // GH_Goo abstract class takes care to implement all the basic functionnality of IGH_Goo.
        // GH_Goo<T> is a generic type where T is the actual Type we are wrapping inside this GH Data Type
        // Here we are wrapping an object StructureObj inside GH_StructureObj to be able to communicate with the Grasshopper User Interface



        #region Properties
        public override Truss Value // The StructureObj object is accessible from the Value property of the GH_StructureObj
        {
            get { return base.Value; }
            set
            {
                base.Value = value;
            }
        }


        #endregion Properties

        #region Formatters

        // Formatting data is primarily a User Interface task.
        // Both the data type and the data state need to be presented in human-readable form every now and again. 
        // This mostly involves readonly (= get only) properties as looking at data does not change its state
        public override bool IsValid { get { return Value.IsValid; } }

        public override string TypeName { get { return Value.TypeName; } }

        public override string TypeDescription { get { return "A structure is composed of finite elements linking the nodes"; } }

        public override string ToString() //return a string representation of the value of this instance
        {
            return Value.ToString();
        }

        #endregion Formatters

        #region Constructors

        public GH_Truss() // default constructor
        {
            Value = new Truss();
        }

        public GH_Truss(Truss structure)   // constructor with initial parameter called in the AssembleStructureComponent Solveinstance method
        {
            Value = structure;
        }
        public GH_Truss(GH_Goo<Truss> GH_structure)  //Copy constructor
        {
            Value = GH_structure.Value;
        }

        public override IGH_Goo Duplicate() //Duplication method calling the copy constructor
        {
            return new GH_Truss(this);
        }

        #endregion Constructors


        #region Methods
        #region Casting
        public override bool CastFrom(object source)
        {
            if (source is Truss)
            {
                Truss s = source as Truss;
                Value = s;
            }
            // Handle the case when a Truss is wrapped in a GH_ObjectWrapper
            if (source is GH_ObjectWrapper wrapper && wrapper.Value is Truss)
            {
                Value = (Truss)wrapper.Value;
                return true;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(ref Q target)
        {

            if (typeof(Q).IsAssignableFrom(typeof(Truss)))
            {
                object structure = Value;
                target = (Q)structure;
                return true;
            }

            target = default;

            return false;
        }
        public override object ScriptVariable() // creates a safe instance of this data to be used inside untrusted code like a C# or VB Script component
        {
            return Value;
        }
        #endregion Casting

        #region Serialization
        public override bool Write(GH_IWriter writer) // Serialize this instance to a Grasshopper writer object.
        {


            return base.Write(writer);
        }
        public override bool Read(GH_IReader reader) //Deserialize this instance from a Grasshopper reader object
        {


            return base.Read(reader);
        }

        #endregion Serialization




        #endregion Methods
    }
}

