import pytest

from ..jeeves import Jeeves
from ..sourcehooks.agency import Agency


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Agency(sourcedata=source)

def test_agency_names_query(resource_a):
    assert 'NONFED' in resource_a.all_names().tolist()

def test_agencies_query_from_lrsegs(resource_a):
    assert 'NONFED' in resource_a.agencycodes_from_lrsegnames(lrsegnames=['N42001PU2_2790_3290']).agencycode.tolist()
