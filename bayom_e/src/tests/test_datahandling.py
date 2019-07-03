import pytest

# from bayom_e.src.data_handling.interface import *
from bayom_e.src.data_handling.data_interface import get_loaded_data_handler_no_objective

@pytest.fixture(scope='module')
def resource_dh_adamsPA(request):
    # Load the data handler
    dh = get_loaded_data_handler_no_objective(geoscale='county',
                                              geoentities=['Adams, PA'],
                                              savedata2file=False,
                                              baseloadingfilename='2010NoActionLoads_20190325.csv')
    return dh

def test_default_County_DataHandler_ADAMSCounty(resource_dh_adamsPA):
    # Verify the lrseg list is populated correctly
    assert 'N42001PU0_3000_3090' in resource_dh_adamsPA.LRSEGS


def test_default_County_DataHandler_NUmberlandVACounty():
    dh = get_loaded_data_handler_no_objective(geoscale='county',
                                              geoentities=['Northumberland, VA'],
                                              savedata2file=False,
                                              baseloadingfilename='2010NoActionLoads_20190325.csv')
    # Verify the lrseg list is populated correctly
    assert dh.lrsegsetlist == ['N51133RL0_6450_0000', 'N51133RL0_6530_0000', 'N51133RL0_6501_0000', 'N51133PL0_6272_0000', 'N51133PL0_6271_0000', 'N51133PL0_6270_0000', 'N51133PL0_6140_0000']


def test_default_County_DataHandler_instantiation_BroomeNYCounty():
    dh = get_loaded_data_handler_no_objective(geoscale='county',
                                              geoentities=['Broome, NY'],
                                              savedata2file=False,
                                              baseloadingfilename='2010NoActionLoads_20190325.csv')
    # Verify the lrseg list is populated correctly
    assert set(dh.lrsegsetlist) == {'N36007SU5_0420_0500', 'N36007SU4_0430_0420', 'N36007SU2_0440_0550', 'N36007SU5_0460_0480', 'N36007SU6_0480_0520', 'N36007SU6_0520_0500', 'N36007SU7_0550_0540', 'N36007SU6_0500_0550', 'N36007SU1_0410_0480', 'N36007SU3_0240_0350', 'N36007SU2_0280_0430', 'N36007SU4_0260_0350', 'N36007SU4_0350_0420'}


def test_default_Lrseg_DataHandler_instantiation():
    dh = get_loaded_data_handler_no_objective(geoscale='lrseg',
                                              geoentities=['N51133RL0_6450_0000'],
                                              savedata2file=False,
                                              baseloadingfilename='2010NoActionLoads_20190325.csv')
    # yo = DataHandlerLrsegWithCostConstraint(savedata2file=False, geoentities=['N51133RL0_6450_0000'])
    # Verify the lrseg list is populated correctly
    assert 'N51133RL0_6450_0000' in dh.LRSEGS

def test_default_Lrseg_DataHandler_inMontgomeryCountyMD():
    dh = get_loaded_data_handler_no_objective(geoscale='lrseg',
                                              geoentities=['N24031PM0_4640_4820'],
                                              savedata2file=False,
                                              baseloadingfilename='2010NoActionLoads_20190325.csv')
    # N24031PM0_4640_4820 = Cabin John Creek, in Montgomery County

    # Verify the lrseg list is populated correctly
    assert 'N24031PM0_4640_4820' in dh.LRSEGS

# def test_default_lrseg_instantiation():
#     lrseg = Lrseg(save2file=False, geolist=['N51133RL0_6450_0000'])  # lrseg in Northumberland County, VA
#
#     # Verify the lrseg list is populated correctly
#     assert 'N51133RL0_6450_0000' in lrseg.lrsegsetlist
#
# def test_default_county_instantiation():
#     county = County(save2file=False, geolist=['Northumberland, VA'])  # lrseg in Northumberland County, VA
#
#     # Verify the lrseg list is populated correctly
#     assert county.lrsegsetlist == ['N51133RL0_6450_0000', 'N51133RL0_6530_0000', 'N51133RL0_6501_0000', 'N51133PL0_6272_0000', 'N51133PL0_6271_0000', 'N51133PL0_6270_0000', 'N51133PL0_6140_0000']
