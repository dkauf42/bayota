import pytest

from ..jeeves import Jeeves
from ..sourcehooks.loadsource import LoadSource


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return LoadSource(sourcedata=source)


def test_loadsources_query_from_lrseg_agency_sectors_contains_LEGUMEHAY(resource_a):
    assert 'Legume Hay' in resource_a.loadsources_from_lrseg_agency_sector(lrsegs=['N42001PU2_2790_3290'],
                                                                           agencies=['NONFED', 'FWS'],
                                                                           sectors=['Agriculture']).loadsource.tolist()


def test_loadsourceshortnames_query_from_fullnames(resource_a):
    assert 'mir' in resource_a.shortnames_from_fullnames(['MS4 Roads'])['loadsourceshortname'].tolist()
