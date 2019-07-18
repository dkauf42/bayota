import pytest
import pandas as pd

from ..jeeves import Jeeves
from ..sourcehooks.sourcehooks import SourceHook


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return SourceHook(sourcedata=source)


def test_singleconvert_returns_single_series(resource_a):
    pass


def test_map_using_a_sourcetable_with_list(resource_a):
    test_values = [10]
    retval = resource_a._map_using_sourcetbl(test_values, tbl='TblAgency',
                                             tocol='agencycode', fromcol='agencyid',
                                             todict=False, flatten=False)
    assert ('nps' in retval) and isinstance(retval, list)


def test_map_using_a_sourcetable_with_series(resource_a):
    test_values = pd.Series([10, 8])
    retval = resource_a._map_using_sourcetbl(test_values, tbl='TblAgency',
                                             tocol='agencycode', fromcol='agencyid',
                                             todict=False, flatten=False)
    assert ('nps' in retval.tolist()) and isinstance(retval, pd.Series)


def test_map_using_a_sourcetable_with_dataframe(resource_a):
    test_values = pd.DataFrame([10, 8], columns=['agencyid'])
    retval = resource_a._map_using_sourcetbl(test_values, tbl='TblAgency',
                                             tocol='agencycode', fromcol='agencyid',
                                             todict=False, flatten=False)
    assert ('nps' in retval['agencycode'].tolist()) and isinstance(retval, pd.DataFrame)


def test_append_ids_to_table(resource_a):
    pass


def test_checkOnlyOne(resource_a):
    pass
