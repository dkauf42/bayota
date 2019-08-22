import pytest

from bayom_e.data_handling.data_interface import get_dataplate


@pytest.fixture(scope='module')
def nlp_dp_2010(request):
    # Load the data handler
    nlp_dp_2010 = get_dataplate(name='nlp', baseloadingfilename='2010NoActionLoads_updated.csv',
                                geoscale='county', geoentities=['Adams, PA'], savedata2file=False)
    return nlp_dp_2010


def test_county_DataPlate_AdamsPA(nlp_dp_2010):
    # Verify the lrseg list is populated correctly
    retval = nlp_dp_2010.LRSEGS
    assert isinstance(retval, list) and \
           ({'N42001PU0_3000_3090', 'N42001PU2_2790_3290', 'N42001PM2_2860_3040',
             'N42001PM3_3040_3340', 'N42001SL3_2460_2430', 'N42001SL3_2400_2440'} == set(retval))

