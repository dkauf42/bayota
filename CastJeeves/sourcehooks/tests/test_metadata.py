import unittest

from CastJeeves.jeeves import Jeeves
from CastJeeves.sourcehooks.metadata import Metadata


class TddForMetadata(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        source = Jeeves.loadInSourceDataFromSQL()
        cls.metadata = Metadata(sourcedata=source)

    def test_correct_metadata(self):
        pass
