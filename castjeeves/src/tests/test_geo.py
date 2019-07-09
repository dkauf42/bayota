import pytest

from ..jeeves import Jeeves
from ..sourcehooks.geo import Geo


@pytest.fixture(scope='module')
def resource_geo(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Geo(sourcedata=source)


def test_correct_countyid_queried_from_AnneArundel_countyname_and_stateabbreviation(resource_geo):
    retval = resource_geo.county.countyid_from_countystatestrs(getfrom=['Adams, PA',
                                                               'Anne Arundel, MD']).countyid.tolist()
    assert 11 in retval


def test_generic_lrsegid_query_returns_correct_from_countystatestrs(resource_geo):
    assert 100 in resource_geo.lrsegids_from(countystatestrs=['Adams, PA', 'Anne Arundel, MD']).lrsegid.tolist()


def test_generic_lrsegid_query_returns_correct_from_lrsegnames(resource_geo):
    assert 741 in resource_geo.lrsegids_from(lrsegnames=['N42001PU2_2790_3290']).lrsegid.tolist()


def test_generic_lrsegid_query_returns_correct_from_countyids(resource_geo):
    assert 100 in resource_geo.lrsegids_from(countyid=[11]).lrsegid.tolist()


def test_generic_lrsegid_query_raises_error_for_more_than_one_keyword_argument(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.lrsegids_from(countystatestrs=['Adams, PA', 'Anne Arundel, MD'],
                                   lrsegnames=['N42001PU2_2790_3290'])


def test_lrsegs_query_from_geoscale_with_names(resource_geo):
    assert 'N42001PU2_2790_3290' in resource_geo.lrseg.names_from_ids(ids=resource_geo.lrsegids_from_geoscale_with_names(scale='County',
                                                                                                       areanames=['Adams, PA']
                                                                                                       )
                                                                      ).landriversegment.tolist()


def test_lrseg_geographyfullnames_query_from_county_state_str(resource_geo):
    geodf = resource_geo.county.add_lrsegs_to_counties(countystatestrs=['Anne Arundel, MD'])

    geodf = resource_geo.lrseg.remove_outofcbws_lrsegs(lrsegdf=geodf)

    geonames = resource_geo.geonames_from_lrsegid(lrsegids=geodf[['lrsegid']])

    assert 'MD-N24003XU3_4650_0001(CBWS)' in list(geonames)


def test_geo_scale_query_contains_COUNTY(resource_geo):
    assert 'County' in resource_geo.all_geotypes().geographytype.tolist()


def test_geo_names_query_using_ID_for_COUNTYID_contains_ANNEARUNDEL(resource_geo):
    assert 'Anne Arundel, MD' in resource_geo.geonames_from_geotypeid(geotype=[2]).tolist()


def test_geo_names_query_using_LRSEGID(resource_geo):
    lrsegids = resource_geo.lrsegids_from_geoscale_with_names(scale='County',
                                                              areanames=['Adams, PA']
                                                              )
    assert 'PA-N42001PU2_2790_3290(CBWS)' in resource_geo.geonames_from_lrsegid(lrsegids=lrsegids).tolist()


def test_geo_names_query_using_ID_raises_error_when_passed_a_name(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.geonames_from_geotypeid(['County'])


def test_geo_names_query_using_name_for_COUNTYID_contains_ANNEARUNDEL(resource_geo):
    assert 'Anne Arundel, MD' in resource_geo.geonames_from_geotypename(geotype=['County']).tolist()


def test_geo_names_query_raises_error_when_specified_scale_does_not_exist(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.geonames_from_geotypeid(['MinorState'])


def test_geo_names_query_raises_error_when_no_scale_specified(resource_geo):
    with pytest.raises(ValueError):
        resource_geo.geonames_from_geotypeid()
