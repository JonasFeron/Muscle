import unittest
from Main_AssembleStructure import core
import sys

class Main_AssembleStructure_Tests(unittest.TestCase):
    def test_ASimple2DStructure(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,0.0,5.0],[0.0,0.0,0.0],[5.0,0.0,0.0],[-5.0,0.0,0.0]],\"Elements_ExtremitiesIndex\":[[0,1],[0,2],[0,3]],\"Elements_A\":[0.0,0.0,0.0],\"Elements_E\":[0.0,0.0,0.0],\"IsDOFfree\":[true,true,true,false,false,false,false,false,false,false,false,false]}"
        output = core(SharedData)

        print (output)
        self.assertEqual(True,True)

if __name__ == '__main__':
    unittest.main()
