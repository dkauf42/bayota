import pytest

from ..jeeves import Jeeves
from ..sourcehooks.metadata import Metadata

# Load the Source Data and Base Condition tables
source = Jeeves.loadInSourceDataFromSQL()
metadata = Metadata(sourcedata=source)


def test_correct_metadata():
        pass
