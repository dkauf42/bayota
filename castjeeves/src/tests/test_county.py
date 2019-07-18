import pytest

from ..jeeves import Jeeves
from ..sourcehooks.county import County


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return County(sourcedata=source)


def test_countyid_query_from_list_of_countystatestrs(resource_a):
    test_values = ['Adams, PA', 'Anne Arundel, MD']
    retval = resource_a.countyid_from_countystatestrs(getfrom=test_values).countyid.tolist()
    assert {11, 194} == set(retval)
