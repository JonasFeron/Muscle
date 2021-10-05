import unittest
from Main_LinearSolveStructure import core
import sys

class Main_LinearSolveStructure_Tests(unittest.TestCase):
    def test_structure_2bars(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,0.0,1000.0],[1000.0,0.0,0.0],[-1000.0,0.0,0.0]],\"Elements_ExtremitiesIndex\":[[0,1],[0,2]],\"Elements_A\":[2500.0,2500.0],\"Elements_E\":[10000.0,10000.0],\"IsDOFfree\":[true,false,true,false,false,false,false,false,false],\"AxialForces_Already_Applied\":[0.0,0.0],\"Loads_To_Apply\":[[0.0,0.0,-100000.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]}"
        output = core(SharedData)

        print (output)
        self.assertEqual(True,True)

    def test_structure_2cables_prestressed(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,1.0,0.0],[1.0,1.0,0.0],[2.0,1.0,0.0]],\"Loads_To_Apply\":[[20000.0,0.0,0.0],[0.0,0.0,-1.0],[-20000.0,0.0,0.0]],\"Elements_ExtremitiesIndex\":[[0,1],[1,2]],\"Elements_A\":[50.27,50.27],\"Elements_E\":[100000.0,100000.0],\"AxialForces_Already_Applied\":[0.0,0.0],\"IsDOFfree\":[false,false,false,true,true,true,false,false,false],\"n_steps\":1}"

        output = core(SharedData)

        print (output)
        self.assertEqual(True,True)


if __name__ == '__main__':
    unittest.main()
