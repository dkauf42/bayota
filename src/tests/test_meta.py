import pytest

from ..jeeves import Jeeves
from ..sourcehooks.meta import Metadata


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    meta = Jeeves.loadInMetaDataFromSQL()
    return Metadata(sourcedata=source, metadata=meta)


def test_costprofilenames_query_contains_watershed(resource_a):
    assert 'Watershed' in resource_a.costprofile_names().tolist()

def test_correct_metadata(resource_a):
        pass
