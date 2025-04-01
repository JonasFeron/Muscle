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
from MusclePyTests.femodel.test_pyelements import TestPyElements
from MusclePyTests.femodel.test_pynodes import TestPyNodes
from MusclePyTests.solvers.linear_dm.test_linear_dm_2bars_truss import TestLinearDM_2BarsTruss
from MusclePyTests.solvers.linear_dm.test_linear_dm_3prestressedcables import TestLinearDM_3PrestressedCables
from MusclePyTests.solvers.nonlinear_dm.test_nonlinear_dm_2bars_truss import TestNonlinearDM_2BarsTruss
from MusclePyTests.solvers.nonlinear_dm.test_nonlinear_dm_loose_mechanism import TestNonlinearDM_LooseMechanism
from MusclePyTests.solvers.nonlinear_dm.test_nonlinear_dm_prestressed_tight_rope import TestNonlinearDM_PrestressedTightRope
from MusclePyTests.solvers.svd.test_svd_2cables import TestSVD2Cables
from MusclePyTests.solvers.svd.test_svd_3cables import TestSVD3Cables
from MusclePyTests.solvers.svd.test_svd_simplex import TestSVDSimplex
from MusclePyTests.solvers.svd.test_self_stress import TestSelfStressModes
# Import Dynamic Relaxation test modules
from MusclePyTests.solvers.dr.test_dr_2cables import TestDR_2Cables
from MusclePyTests.solvers.dr.test_dr_3simplecables import TestDR_3SimpleCables
from MusclePyTests.solvers.dr.test_dr_3complexcables import TestDR_3ComplexCables
from MusclePyTests.solvers.dr.test_dr_simplex import TestDR_Simplex


def create_test_suite():
    """Create a test suite containing all tests."""
    # Create a test suite
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPyElements))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestPyNodes))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinearDM_2BarsTruss))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestLinearDM_3PrestressedCables))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNonlinearDM_2BarsTruss))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNonlinearDM_LooseMechanism))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestNonlinearDM_PrestressedTightRope))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSVD2Cables))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSVD3Cables))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSVDSimplex))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSelfStressModes))
    # Add Dynamic Relaxation test classes
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDR_2Cables))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDR_3SimpleCables))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDR_3ComplexCables))
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(TestDR_Simplex))

    
    return suite

if __name__ == '__main__':
    # Create and run the test suite
    suite = create_test_suite()
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Exit with non-zero code if tests failed
    sys.exit(not result.wasSuccessful())
