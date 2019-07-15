import pytest
import pandas as pd

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

def test_agencyfullname_from_id(resource_a):
    assert 'Non-Federal' in resource_a.fullnames_from_ids([9])['agencyfullname'][0]

def test_agencyid_query_from_a_list_of_agencycodes(resource_a):
    retval = resource_a.ids_from_names(['gsa', 'nasa'])
    assert ({7, 8} == set(retval)) and isinstance(retval, list)

def test_agencyid_query_from_a_DataFrame_of_agencycodes(resource_a):
    test_df = pd.DataFrame(['gsa', 'nasa'], columns=['agencycode'])
    retval = resource_a.ids_from_names(test_df)
    assert (8 in retval['agencyid'].tolist()) and isinstance(retval, pd.DataFrame)

def test_agencyid_query_from_a_Series_of_agencycodes(resource_a):
    test_series = pd.Series(['gsa', 'nasa'])
    retval = resource_a.ids_from_names(test_series)
    assert (8 in retval.tolist()) and isinstance(retval, pd.Series)

def test_agencyid_from_name(resource_a):
    print(resource_a.ids_from_fullnames(['Non-Federal'])['agencyid'][0])
    assert 9 in resource_a.ids_from_fullnames(['Non-Federal'])['agencyid'].tolist()

