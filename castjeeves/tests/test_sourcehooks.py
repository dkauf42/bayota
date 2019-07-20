import pytest
import pandas as pd
from io import StringIO

from castjeeves.sourcehooks import SourceHook


@pytest.fixture(scope='module')
def resource_a(request, source_resource):
    return SourceHook(sourcedata=source_resource)


@pytest.fixture(scope='module')
def onetoonetbl(request):
    strtbl = """A,B
                aval1,bval1
                aval2,bval2
                aval3,bval3
                aval4,bval4
             """
    testdata = StringIO('\n'.join(strtbl.split()))
    return pd.read_csv(testdata)


@pytest.fixture(scope='module')
def onetomanytbl(request):
    strtbl = """A,B
                aval1,bval1
                aval2,bval2a
                aval2,bval2b
                aval3,bval3a
                aval3,bval3b
                aval3,bval3c
                aval4,bval4
             """
    testdata = StringIO('\n'.join(strtbl.split()))
    return pd.read_csv(testdata)


def test_singleconvert_returns_single_series(resource_a):
    pass


def test_one_to_one_example_map_with_list(resource_a, onetoonetbl):
    test_values = ['aval2']
    retval = resource_a._map_LIST_using_sourcetbl(test_values, sourcetable=onetoonetbl,
                                                  tocol='B', fromcol='A',
                                                  todict=False, flatten_to_set=False)
    assert ({'bval2'} == set(retval)) and isinstance(retval, list)


def test_one_to_one_example_map_with_Series(resource_a, onetoonetbl):
    test_values = pd.Series(['aval2'])
    retval = resource_a._map_SERIES_using_sourcetbl(test_values, sourcetable=onetoonetbl,
                                                    tocol='B', fromcol='A',
                                                    todict=False, flatten_to_set=False)
    assert ({'bval2'} == set(retval.values)) and isinstance(retval, pd.Series)


def test_one_to_one_example_map_with_DataFrame(resource_a, onetoonetbl):
    test_values = pd.DataFrame(['aval2'], columns=['A'])
    retval = resource_a._map_DATAFRAME_using_sourcetbl(test_values, sourcetable=onetoonetbl,
                                                       tocol='B', fromcol='A',
                                                       todict=False, flatten_to_set=False)
    assert ({'bval2'} == set(retval.to_numpy().flatten())) and isinstance(retval, pd.DataFrame)


def test_one_to_many_example_map_with_single_value_list_and_todict(resource_a, onetomanytbl):
    test_values = ['aval3']
    retval = resource_a._map_LIST_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                  tocol='B', fromcol='A',
                                                  todict=True, flatten_to_set=False)
    assert (['bval3a', 'bval3b', 'bval3c'] == retval[test_values[0]]) \
           and isinstance(retval, dict)


def test_one_to_many_example_map_with_single_value_Series_and_todict(resource_a, onetomanytbl):
    test_values = pd.Series(['aval3'])
    retval = resource_a._map_SERIES_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                    tocol='B', fromcol='A',
                                                    todict=True, flatten_to_set=False)
    assert (['bval3a', 'bval3b', 'bval3c'] == retval[test_values[0]]) \
           and isinstance(retval, dict)


def test_one_to_many_example_map_with_single_value_DataFrame_and_todict(resource_a, onetomanytbl):
    test_values = pd.DataFrame(['aval3'], columns=['A'])
    retval = resource_a._map_DATAFRAME_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                       tocol='B', fromcol='A',
                                                       todict=True, flatten_to_set=False)
    assert (['bval3a', 'bval3b', 'bval3c'] == retval[test_values['A'][0]]) \
           and isinstance(retval, dict)


def test_one_to_many_example_map_with_list_and_todict(resource_a, onetomanytbl):
    test_values = ['aval2', 'aval3']
    retval = resource_a._map_LIST_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                  tocol='B', fromcol='A',
                                                  todict=True, flatten_to_set=False)
    assert (['bval2a', 'bval2b'] == retval[test_values[0]]) \
           and (['bval3a', 'bval3b', 'bval3c'] == retval[test_values[1]]) \
           and isinstance(retval, dict)


def test_one_to_many_example_map_with_Series_and_todict(resource_a, onetomanytbl):
    test_values = pd.Series(['aval2', 'aval3'])
    retval = resource_a._map_SERIES_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                    tocol='B', fromcol='A',
                                                    todict=True, flatten_to_set=False)
    assert (['bval2a', 'bval2b'] == retval[test_values[0]]) \
           and (['bval3a', 'bval3b', 'bval3c'] == retval[test_values[1]]) \
           and isinstance(retval, dict)


def test_one_to_many_example_map_with_DataFrame_and_todict(resource_a, onetomanytbl):
    test_values = pd.DataFrame(['aval2', 'aval3'], columns=['A'])
    retval = resource_a._map_DATAFRAME_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                    tocol='B', fromcol='A',
                                                    todict=True, flatten_to_set=False)
    assert (['bval2a', 'bval2b'] == retval[test_values['A'][0]]) \
           and (['bval3a', 'bval3b', 'bval3c'] == retval[test_values['A'][1]]) \
           and isinstance(retval, dict)


def test_one_to_many_example_map_with_single_value_list_and_flattened(resource_a, onetomanytbl):
    test_values = ['aval3']
    retval = resource_a._map_LIST_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                  tocol='B', fromcol='A',
                                                  todict=False, flatten_to_set=True)
    assert ({'bval3a', 'bval3b', 'bval3c'} == retval) and isinstance(retval, set)


def test_one_to_many_example_map_with_multivalue_list_and_flattened(resource_a, onetomanytbl):
    test_values = ['aval2', 'aval3']
    retval = resource_a._map_LIST_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                  tocol='B', fromcol='A',
                                                  todict=False, flatten_to_set=True)
    assert ({'bval2a', 'bval2b', 'bval3a', 'bval3b', 'bval3c'} == retval) and isinstance(retval, set)


def test_one_to_many_example_map_with_multivalue_Series_and_flattened(resource_a, onetomanytbl):
    test_values = pd.Series(['aval2', 'aval3'])
    retval = resource_a._map_SERIES_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                    tocol='B', fromcol='A',
                                                    todict=False, flatten_to_set=True)
    assert ({'bval2a', 'bval2b', 'bval3a', 'bval3b', 'bval3c'} == retval) and isinstance(retval, set)


def test_one_to_many_example_map_with_multivalue_DataFrame_and_flattened(resource_a, onetomanytbl):
    test_values = pd.DataFrame(['aval2', 'aval3'], columns=['A'])
    retval = resource_a._map_DATAFRAME_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                                    tocol='B', fromcol='A',
                                                    todict=False, flatten_to_set=True)
    assert ({'bval2a', 'bval2b', 'bval3a', 'bval3b', 'bval3c'} == retval) and isinstance(retval, set)


def test_one_to_many_with_list_raises_error_without_todict_or_flatten(resource_a, onetomanytbl):
    with pytest.raises(ValueError):
        test_values = ['aval2']
        resource_a._map_LIST_using_sourcetbl(test_values, sourcetable=onetomanytbl,
                                             tocol='B', fromcol='A',
                                             todict=False, flatten_to_set=False)


def test_append_ids_to_table(resource_a):
    pass


def test_checkOnlyOne(resource_a):
    pass
