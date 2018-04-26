import unittest

from sandbox.util.Jeeves.sourcehooks import SourceHook


class TddForSourceHook(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.sourcehook = SourceHook()

    def test_singleconvert_returns_single_series(self):
        pass

    def test_append_ids_to_table(self):
        pass

    def test_checkOnlyOne(self):
        pass
