import pytest
import pandas as pd

from castjeeves.sourcehooks import Sector


@pytest.fixture(scope='module')
def resource_a(request, source_resource):
    return Sector(sourcedata=source_resource)


def test_sector_all_names_query_as_list(resource_a):
    retval = resource_a.all_names(astype=list)
    assert ('Agriculture' in retval) and isinstance(retval, list)


def test_sector_all_names_query_as_Series(resource_a):
    retval = resource_a.all_names(astype='series')
    assert ('Agriculture' in retval.tolist()) and isinstance(retval, pd.Series)
