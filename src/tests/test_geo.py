import pytest

from ..jeeves import Jeeves
from ..sourcehooks.geo import Geo


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Geo(sourcedata=source)

def test_correct_countyid_queried_from_AnneArundel_countyname_and_stateabbreviation(resource_a):
    assert 11 in resource_a.county.countyid_from_countystatestrs(getfrom=['Adams, PA',
                                                                         'Anne Arundel, MD']).countyid.tolist()


def test_generic_lrsegid_query_returns_correct_from_countystatestrs(resource_a):
    assert 100 in resource_a.lrsegids_from(countystatestrs=['Adams, PA', 'Anne Arundel, MD']).lrsegid.tolist()


def test_generic_lrsegid_query_returns_correct_from_lrsegnames(resource_a):
    assert 741 in resource_a.lrsegids_from(lrsegnames=['N42001PU2_2790_3290']).lrsegid.tolist()


def test_generic_lrsegid_query_returns_correct_from_countyids(resource_a):
    assert 100 in resource_a.lrsegids_from(countyid=[11]).lrsegid.tolist()


def test_generic_lrsegid_query_raises_error_for_more_than_one_keyword_argument(resource_a):
    with pytest.raises(ValueError):
        resource_a.lrsegids_from(countystatestrs=['Adams, PA', 'Anne Arundel, MD'],
                          lrsegnames=['N42001PU2_2790_3290'])


def test_lrsegs_query_from_geoscale_with_names(resource_a):
    assert 'N42001PU2_2790_3290' in resource_a.lrseg.names_from_ids(ids=resource_a.lrsegids_from_geoscale_with_names(scale='County',
                                                                                                       areanames=['Adams, PA']
                                                                                                       )
                                                             ).landriversegment.tolist()


def test_geo_scale_query_contains_COUNTY(resource_a):
    assert 'County' in resource_a.all_geotypes().geographytype.tolist()


def test_geo_names_query_using_ID_for_COUNTYID_contains_ANNEARUNDEL(resource_a):
    assert 'Anne Arundel, MD' in resource_a.geonames_from_geotypeid(geotype=[2]).tolist()


def test_geo_names_query_using_ID_raises_error_when_passed_a_name(resource_a):
    with pytest.raises(ValueError):
        resource_a.geonames_from_geotypeid(['County'])


def test_geo_names_query_using_name_for_COUNTYID_contains_ANNEARUNDEL(resource_a):
    assert 'Anne Arundel, MD' in resource_a.geonames_from_geotypename(geotype=['County']).tolist()


def test_geo_names_query_raises_error_when_specified_scale_does_not_exist(resource_a):
    with pytest.raises(ValueError):
        resource_a.geonames_from_geotypeid(['MinorState'])


def test_geo_names_query_raises_error_when_no_scale_specified(resource_a):
    with pytest.raises(ValueError):
        resource_a.geonames_from_geotypeid()
