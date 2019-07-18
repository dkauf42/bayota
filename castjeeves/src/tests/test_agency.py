import pytest
import pandas as pd

from ..jeeves import Jeeves
from ..sourcehooks.agency import Agency


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Agency(sourcedata=source)

def test_agency_all_names_query_as_list(resource_a):
    retval = resource_a.all_names(astype=list)
    assert ('nonfed' in retval) and isinstance(retval, list)

def test_agency_all_names_query_as_Series(resource_a):
    retval = resource_a.all_names(astype='series')
    assert ('nonfed' in retval.tolist()) and isinstance(retval, pd.Series)

def test_agencies_query_from_lrsegs(resource_a):
    test_values = ['N42001PU2_2790_3290']
    retval = resource_a.agencycodes_from_lrsegnames(lrsegnames=test_values)
    assert 'nonfed' in retval

def test_agencyfullname_query_from_a_list_of_agencyid(resource_a):
    test_values = [9]
    retval = resource_a.fullnames_from_ids(test_values)
    assert 'Non-Federal' in retval

def test_agencyid_query_from_a_list_of_agencycodes(resource_a):
    test_values = ['gsa', 'nasa']
    retval = resource_a.ids_from_names(test_values)
    assert ({7, 8} == set(retval)) and isinstance(retval, list)

def test_agencyid_query_from_a_DataFrame_of_agencycodes(resource_a):
    test_values = pd.DataFrame(['gsa', 'nasa'], columns=['agencycode'])
    retval = resource_a.ids_from_names(test_values)
    assert (8 in retval['agencyid'].tolist()) and isinstance(retval, pd.DataFrame)

def test_agencyid_query_from_a_Series_of_agencycodes(resource_a):
    test_values = pd.Series(['gsa', 'nasa'])
    retval = resource_a.ids_from_names(test_values)
    assert (8 in retval.tolist()) and isinstance(retval, pd.Series)

def test_agencyid_query_from_a_list_of_agencyfullnames(resource_a):
    test_values = ['Non-Federal']
    retval = resource_a.ids_from_fullnames(test_values)
    assert (9 in retval) and isinstance(retval, list)

