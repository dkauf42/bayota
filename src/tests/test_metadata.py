import pytest

from ..jeeves import Jeeves
from ..sourcehooks.metadata import Metadata

# # Load the Source Data and Base Condition tables
# source = Jeeves.loadInSourceDataFromSQL()
# metadata = Metadata(sourcedata=source)

@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Metadata(sourcedata=source)


def test_correct_metadata(resource_a):
        pass
