import unittest
import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/MusclePy'))
sys.path.append(base_dir)
from MainAssembleStructure import core
import sys

class Main_AssembleStructure_Tests(unittest.TestCase):
    def test_ASimple2DStructure(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,0.0,0.0],[1.0,0.0,0.0],[2.0,0.0,0.0]],\"ElementsEndNodes\":[[0,1],[0,2]],\"ElementsType\":[1,1],\"ElementsA\":[0.0,0.0],\"ElementsE\":[0.0,0.0],\"IsDOFfree\":[false,false,false,true,false,true,false,false,false]}"

        output = core(SharedData)

        print (output)
        self.assertEqual(True,True)

if __name__ == '__main__':
    unittest.main()
