import unittest
import os
import sys

# Add source directory to Python path
base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src/MusclePy'))
sys.path.append(base_dir)

# Import all test modules
from femodel.test_fem_elements import TestFEMElements
from femodel.test_fem_nodes import TestFEMNodes
from solvers.main_linear_dm.test_main_linear_dm_2bars_truss import TestMainLinearDM_2BarsTruss
from solvers.main_linear_dm.test_main_linear_dm_3prestressedcables import TestMainLinearDM_3PrestressedCables

def create_test_suite():
    """Create a test suite containing all tests."""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFEMElements))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFEMNodes))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMainLinearDM_2BarsTruss))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestMainLinearDM_3PrestressedCables))
    
    return suite

if __name__ == '__main__':
    # Create and run the test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
