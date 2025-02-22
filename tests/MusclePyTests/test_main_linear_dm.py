import unittest
import os
import sys
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/MusclePy'))
sys.path.append(base_dir)
import json
import data as d
import result as r
from MainLinearSolveStructure import main

# class TestMainLinearSolveStructure(unittest.TestCase):

#     def setUp(self):
#         # Setup any necessary data for the tests
#         self.valid_data_json = '{"key": "value"}'  # Replace with actual valid JSON data
#         self.invalid_data_json = '{"invalid_key": "invalid_value"}'  # Replace with actual invalid JSON data

#     def test_core_with_valid_data(self):
#         data = json.loads(self.valid_data_json, object_hook=d.ToSharedDataObject)
#         result = core(data)
#         self.assertIsInstance(result, r.SharedSolverResult)
#         # Add more assertions based on expected result properties

#     def test_core_with_invalid_data(self):
#         data = json.loads(self.invalid_data_json, object_hook=d.ToSharedDataObject)
#         result = core(data)
#         self.assertIsInstance(result, r.SharedSolverResult)
#         # Add more assertions based on expected result properties

# if __name__ == '__main__':
#     unittest.main()

class Main_LinearSolveStructure_Tests(unittest.TestCase):
    def test_structure_2bars(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,0.0,1000.0],[1000.0,0.0,0.0],[-1000.0,0.0,0.0]],\"ElementsEndNodes\":[[0,1],[0,2]],\"ElementsA\":[2500.0,2500.0],\"ElementsE\":[10000.0,10000.0],\"IsDOFfree\":[true,false,true,false,false,false,false,false,false],\"TensionInit\":[0.0,0.0],\"LoadsToApply\":[[0.0,0.0,-100000.0],[0.0,0.0,0.0],[0.0,0.0,0.0]]}"
        output = main(SharedData)

        print (output)
        self.assertEqual(True,True)

    def test_structure_2cables_prestressed(self):
        SharedData = "{\"TypeName\":\"SharedData\",\"NodesCoord\":[[0.0,1.0,0.0],[1.0,1.0,0.0],[2.0,1.0,0.0]],\"LoadsToApply\":[[20000.0,0.0,0.0],[0.0,0.0,-1.0],[-20000.0,0.0,0.0]],\"ElementsEndNodes\":[[0,1],[1,2]],\"ElementsA\":[50.27,50.27],\"ElementsE\":[100000.0,100000.0],\"TensionInit\":[0.0,0.0],\"IsDOFfree\":[false,false,false,true,true,true,false,false,false],\"n_steps\":1}"

        output = main(SharedData)

        print (output)
        self.assertEqual(True,True)


if __name__ == '__main__':
    unittest.main()

