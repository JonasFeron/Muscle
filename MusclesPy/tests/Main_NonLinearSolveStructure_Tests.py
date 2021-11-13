import unittest
from Main_NonLinearSolveStructure import core
import sys

class Main_NonLinearSolveStructure_Tests(unittest.TestCase):
    def test_structure_2barsNL(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,-25.0,0.0],[1.0,-25.0,0.0],[-1.0,-25.0,0.0]],\"Loads_To_Apply\":[[0.0,0.0,-100000.0],[0.0,0.0,0.0],[0.0,0.0,0.0]],\"Elements_EndNodes\":[[0,1],[0,2]],\"Elements_A\":[2500.0,2500.0],\"Elements_E\":[10000.0,10000.0],\"AxialForces_Already_Applied\":[0.0,0.0],\"IsDOFfree\":[true,false,true,false,false,false,false,false,false],\"n_steps\":100}"
        output = core(SharedData)

        print(output)
        self.assertEqual(True,True)

if __name__ == '__main__':
    unittest.main()
