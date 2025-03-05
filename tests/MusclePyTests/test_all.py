import unittest
import os
import sys

# Add source directory to Python path
src_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.append(src_dir)

# Add tests directory to Python path
tests_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(tests_dir)

# Import all test modules
from MusclePyTests.femodel.test_fem_elements import TestFEMElements
from MusclePyTests.femodel.test_fem_nodes import TestFEMNodes
from MusclePyTests.solvers.linear_dm.test_linear_dm_2bars_truss import TestLinearDM_2BarsTruss
from MusclePyTests.solvers.linear_dm.test_linear_dm_3prestressedcables import TestLinearDM_3PrestressedCables

def create_test_suite():
    """Create a test suite containing all tests."""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFEMElements))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestFEMNodes))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinearDM_2BarsTruss))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinearDM_3PrestressedCables))
    
    return suite

if __name__ == '__main__':
    # Create and run the test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
