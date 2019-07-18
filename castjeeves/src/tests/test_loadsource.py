import pytest
import pandas as pd

from ..jeeves import Jeeves
from ..sourcehooks.loadsource import LoadSource


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return LoadSource(sourcedata=source)

def test_loadsource_all_names_query_as_list(resource_a):
    retval = resource_a.all_names(astype=list)
    assert ('lhy' in retval) and isinstance(retval, list)

def test_loadsource_all_names_query_as_Series(resource_a):
    retval = resource_a.all_names(astype='series')
    assert ('aop' in retval.tolist()) and isinstance(retval, pd.Series)

def test_loadsources_query_from_lrseg_agency_sectors_contains_LEGUMEHAY(resource_a):
    retval = resource_a.loadsources_from_lrseg_agency_sector(lrsegs=['N42001PU2_2790_3290'],
                                                             agencies=['nonfed', 'fws'],
                                                             sectors=['Agriculture']).loadsource.tolist()
    assert 'Leguminous Hay' in retval


def test_loadsourceshortnames_query_from_fullnames(resource_a):
    assert 'mir' in resource_a.shortnames_from_fullnames(['MS4 Roads'])['loadsourceshortname'].tolist()
