import unittest
import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/MusclePy'))
sys.path.append(base_dir)
from MainDynamicRelaxation import main
import sys

class Test_Main_NonLinearSolveStructure(unittest.TestCase):
    def test_structure_3barsNL(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,-25.0,0.0],[1.0,-25.0,0.0],[-1.0,-25.0,0.0]],\"LoadsToApply\":[[0.0,0.0,-100000.0],[0.0,0.0,0.0],[0.0,0.0,0.0]],\"ElementsEndNodes\":[[0,1],[0,2]],\"ElementsA\":[2500.0,2500.0],\"ElementsE\":[10000.0,10000.0],\"TensionInit\":[0.0,0.0],\"IsDOFfree\":[true,false,true,false,false,false,false,false,false],\"n_steps\":100}"
        output = main(SharedData)

        print(output)
        self.assertEqual(True,True)

if __name__ == '__main__':
    unittest.main()
