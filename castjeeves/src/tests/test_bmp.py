import pytest

from ..jeeves import Jeeves
from ..sourcehooks.bmp import Bmp


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Bmp(sourcedata=source)

def test_names_query_contains_GRASSBUFFERS(resource_a):
    assert 'GrassBuffers' in resource_a.all_names().tolist()

def test_efficiency_table_has_bmp_column(resource_a):
    assert 'bmpid' in resource_a.bmp_efficiencies().columns.tolist()

def test_bmpid_query_from_a_list_of_shortnames(resource_a):
    test_values = ['watercontstruc']
    retval = resource_a.ids_from_names(test_values)
    assert 36 in retval
