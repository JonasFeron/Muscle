using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using GH_IO.Serialization;
using Grasshopper.Kernel.Data;
using Grasshopper.Kernel.Types;
using Rhino.Geometry;


namespace Muscle.Structure
{

    public class GH_StructureObj : GH_Goo<StructureObj>
    {
        // All data used in Grasshopper must implement the IGH_Goo interface. 
        // IGH_Goo defines the bare minimum of methods and properties for any kind of data before it is allowed to play ball
        // GH_Goo abstract class takes care to implement all the basic functionnality of IGH_Goo.
        // GH_Goo<T> is a generic type where T is the actual Type we are wrapping inside this GH Data Type
        // Here we are wrapping an object StructureObj inside GH_StructureObj to be able to communicate with the Grasshopper User Interface



        #region Properties
        public override StructureObj Value // The StructureObj object is accessible from the Value property of the GH_StructureObj
        {
            get { return base.Value; }
            set
            {
                base.Value = value;
            }
        }

        // on veut également transformer notre Objet StructureObj qui utilise des data de type Rhino.Geometry (Point 3D, Line,...) et de type System.Collections.Generic (list, Dictionnaries) 
        // En un objet GH_StructureObj qui utilise des data de type Grasshopper.Kernel.Types (GH_Point, GH_line, GH_Structure<T>,...) 
        // un objet StructureObj permet de manipuler les données ou faire des calculs
        // un objet GH_StructureObj permet de les afficher et communiquer au sein de GH.
        // Donc toutes les données de la géométrie qu'on veut pouvoir manipuler//afficher au sein de GH doivent être converties en donnée de type GH


        #endregion Properties

        #region Formatters

        // Formatting data is primarily a User Interface task.
        // Both the data type and the data state need to be presented in human-readable form every now and again. 
        // This mostly involves readonly (= get only) properties as looking at data does not change its state
        public override bool IsValid { get { return Value.IsValid; } }

        public override string TypeName { get { return Value.TypeName; } }

        public override string TypeDescription { get { return "StructureObj object is composed of Lines linking the nodes"; } }

        public override string ToString() //return a string representation of the value of this instance
        {
            return Value.ToString();
        }

        #endregion Formatters

        #region Constructors

        public GH_StructureObj() // default constructor
        {
            Value = new StructureObj();
        }

        public GH_StructureObj(StructureObj structure)   // constructor with initial parameter called in the AssembleStructureComponent Solveinstance method
        {
            Value = structure;
        }
        public GH_StructureObj(GH_Goo<StructureObj> GH_structure)  //Copy constructor
        {
            Value = GH_structure.Value;
        }

        public override IGH_Goo Duplicate() //Duplication method calling the copy constructor
        {
            return new GH_StructureObj(this);
        }

        #endregion Constructors


        #region Methods
        #region Casting
        public override bool CastFrom(object source)
        {
            if (source is StructureObj)
            {
                StructureObj s = source as StructureObj;
                Value = s;
            }

            return base.CastFrom(source);
        }

        public override bool CastTo<Q>(ref Q target)
        {

            if (typeof(Q).IsAssignableFrom(typeof(StructureObj)))
            {
                object structure = Value;
                target = (Q)structure;
                return true;
            }

            target = default(Q);

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
            //writer.SetString("type name", Value.ShapeName);
            //writer.Setdouble("dimension", Value.Dimension);
            //writer.Setdouble("thickness", Value.Thickness);

            //new GH_StructuralMaterial(Value.Material).Write(writer);


            return base.Write(writer);
        }
        public override bool Read(GH_IReader reader) //Deserialize this instance from a Grasshopper reader object
        {
            //string TypeName = reader.GetString("type name");

            //if (TypeName == "Circle cross section")
            //{
            //    double diameter = reader.Getdouble("dimension");
            //    double thickness = reader.Getdouble("thickness");
            //    GH_StructuralMaterial ghMaterial = new GH_StructuralMaterial();
            //    ghMaterial.Read(reader);
            //    Value = new CircleCrossSection(diameter, thickness, ghMaterial.Value);
            //}
            //else if (TypeName == "Square cross section")
            //{
            //    double diameter = reader.Getdouble("dimension");
            //    double thickness = reader.Getdouble("thickness");
            //    GH_StructuralMaterial ghMaterial = new GH_StructuralMaterial();
            //    ghMaterial.Read(reader);
            //    Value = new SquareCrossSection(diameter, thickness, ghMaterial.Value);
            //}
            //else { return false; }


            return base.Read(reader);
        }

        #endregion Serialization




        #endregion Methods
    }
}

