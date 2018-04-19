import unittest

from sandbox.sandboxer import main


class TddForMain(unittest.TestCase):

    def setUp(self):
        pass

    def test_main_testcase1_runs_to_end_with_valid_arguments(self):
        self.assertTrue(main(numinstances=1, testcase=1).successful_creation_log)

    def test_main_testcase2_runs_to_end_with_valid_arguments(self):
        self.assertTrue(main(numinstances=1, testcase=2).successful_creation_log)

    def test_main_testcase3_runs_to_end_with_valid_arguments(self):
        self.assertTrue(main(numinstances=1, testcase=3).successful_creation_log)

    def test_main_raises_error_with_invalid_argument_values(self):
        self.assertRaises(ValueError, main, numinstances=1, testcase=5)
