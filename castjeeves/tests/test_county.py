import pytest
import pandas as pd

from castjeeves.jeeves import Jeeves
from castjeeves.sourcehooks import County


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return County(sourcedata=source)


def test_countyid_query_from_LIST_of_countystatestrs(resource_a):
    test_values = ['Adams, PA', 'Anne Arundel, MD']
    retval = resource_a.countyid_from_countystatestrs(getfrom=test_values)
    assert {11, 194} == set(retval) and isinstance(retval, list)


def test_countyid_query_from_SERIES_of_countystatestrs(resource_a):
    test_values = pd.Series(['Adams, PA', 'Anne Arundel, MD'])
    retval = resource_a.countyid_from_countystatestrs(getfrom=test_values)
    assert {11, 194} == set(retval) and isinstance(retval, pd.Series)


def test_all_names_query_contains_AnneArundel_as_list(resource_a):
    retval = resource_a.all_names(astype=list)
    assert ('Anne Arundel' in retval) and isinstance(retval, list)


def test_all_names_query_contains_AnneArundel_as_Series(resource_a):
    retval = resource_a.all_names(astype='series')
    assert ('Anne Arundel' in retval.tolist()) and isinstance(retval, pd.Series)
