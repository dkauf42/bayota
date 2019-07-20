import pytest

from castjeeves.jeeves import Jeeves
from castjeeves.sourcehooks import Geo


@pytest.fixture(scope='module')
def resource_geo(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Geo(sourcedata=source)


def test_generic_lrsegid_query_returns_correct_from_countystatestrs_list(resource_geo):
    test_values = ['Adams, PA', 'Anne Arundel, MD']
    retval = resource_geo.lrsegids_from(countystatestrs=test_values)
    assert (100 in retval) and isinstance(retval, list)


def test_generic_lrsegid_query_returns_correct_from_lrsegnames_list(resource_geo):
    test_values = ['N42001PU2_2790_3290']
    retval = resource_geo.lrsegids_from(lrsegnames=test_values)
    assert (741 in retval) and isinstance(retval, list)


def test_generic_lrsegid_query_returns_correct_from_countyids_list(resource_geo):
    test_values = [11]
    retval = resource_geo.lrsegids_from(countyid=test_values)
    assert (100 in retval) and isinstance(retval, list)


def test_generic_lrsegid_query_raises_error_for_more_than_one_keyword_argument(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.lrsegids_from(countystatestrs=['Adams, PA', 'Anne Arundel, MD'],
                                   lrsegnames=['N42001PU2_2790_3290'])


def test_lrsegs_query_from_geoscale_with_single_county_name_in_a_list(resource_geo):
    test_values = ['Adams, PA']
    intermediate_lrsegids = resource_geo.lrsegids_from_geoscale_with_names(scale='County', areanames=test_values)
    retval = resource_geo.lrseg.names_from_ids(ids=intermediate_lrsegids)
    assert ('N42001PU2_2790_3290' in retval) and isinstance(retval, list)


def test_lrsegs_query_from_Northumberland_county(resource_geo):
    test_values = ['Northumberland, VA']
    intermediate_lrsegids = resource_geo.lrsegids_from_geoscale_with_names(scale='County', areanames=test_values)
    retval = resource_geo.lrseg.names_from_ids(ids=intermediate_lrsegids)
    assert isinstance(retval, list) and \
           set(retval) == {'N51133RL0_6450_0000', 'N51133RL0_6530_0000', 'N51133RL0_6501_0000',
                           'N51133PL0_6272_0000', 'N51133PL0_6271_0000', 'N51133PL0_6270_0000',
                           'N51133PL0_6140_0000'}


def test_lrsegs_query_from_geoscale_with_county_names_in_a_list(resource_geo):
    test_values = ['Adams, PA', 'Anne Arundel, MD']
    intermediate_lrsegids = resource_geo.lrsegids_from_geoscale_with_names(scale='County', areanames=test_values)
    retval = resource_geo.lrseg.names_from_ids(ids=intermediate_lrsegids)
    assert ('N24003XL3_4710_0000' in retval) and ('N42001PU2_2790_3290' in retval) and isinstance(retval, list)


def test_lrseg_geographyfullnames_query_from_county_state_str(resource_geo):
    test_values = ['Anne Arundel, MD']

    intermediate_geodf = resource_geo.county.add_lrsegs_to_counties(countystatestrs=test_values)
    intermediate_geodf = resource_geo.lrseg.remove_outofcbws_lrsegs(lrsegdf=intermediate_geodf)
    intermediate_lrsegid_list = intermediate_geodf.loc[:, 'lrsegid'].to_list()
    retval = resource_geo.geonames_from_lrsegid(lrsegids=intermediate_lrsegid_list)

    assert ('MD-N24003XU3_4650_0001(CBWS)' in retval) and isinstance(retval, list)


def test_geo_scale_query_contains_COUNTY(resource_geo):
    assert 'County' in resource_geo.all_geotypes().geographytype.tolist()


def test_geo_names_query_using_ID_for_COUNTYID_contains_ANNEARUNDEL(resource_geo):
    test_values = [2]
    retval = resource_geo.geonames_from_geotypeid(geotype=test_values).tolist()
    assert 'Anne Arundel, MD' in retval


def test_geo_names_query_using_LRSEGID(resource_geo):
    test_values = ['Adams, PA']
    intermediate_lrsegids = resource_geo.lrsegids_from_geoscale_with_names(scale='County', areanames=test_values)
    retval = resource_geo.geonames_from_lrsegid(lrsegids=intermediate_lrsegids)
    assert ('PA-N42001PU2_2790_3290(CBWS)' in retval) and isinstance(retval, list)


def test_geo_names_query_using_ID_raises_error_when_passed_a_name(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.geonames_from_geotypeid(['County'])


def test_geo_names_query_using_name_for_COUNTYID_contains_ANNEARUNDEL(resource_geo):
    test_values = ['County']
    retval = resource_geo.geonames_from_geotypename(geotype=test_values).tolist()
    assert 'Anne Arundel, MD' in retval


def test_geo_names_query_raises_error_when_specified_scale_does_not_exist(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.geonames_from_geotypeid(['MinorState'])


def test_geo_names_query_raises_error_when_no_scale_specified(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.geonames_from_geotypeid()
