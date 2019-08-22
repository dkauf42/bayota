import pytest

from castjeeves.jeeves import Jeeves
from castjeeves.sourcehooks import Meta


@pytest.fixture(scope='module')
def resource_a(request, source_resource):
    # Load the MetaData tables
    meta = Jeeves.loadInMetaDataFromSQL()
    return Meta(sourcedata=source_resource, metadata=meta)


def test_costprofilenames_query_contains_watershed(resource_a):
    assert 'Watershed' in resource_a.costprofile_names().tolist()


def test_correct_metadata(resource_a):
        pass
