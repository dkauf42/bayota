import pytest

from efficiencysubproblem.src.data_handling.interface import *


def test_default_CountyWithCostConstraint_instantiation_ADAMSCounty():
    yo = DataHandlerCountyWithCostConstraint(savedata2file=False, geoentities=['Adams, PA'])
    # Verify the lrseg list is populated correctly
    assert 'N42001PU0_3000_3090' in yo.LRSEGS


def test_default_CountyWithCostConstraint_instantiation_NUmberlandVACounty():
    county = DataHandlerCountyWithCostConstraint(savedata2file=False, geoentities=['Northumberland, VA'])
    # Verify the lrseg list is populated correctly
    assert county.lrsegsetlist == ['N51133RL0_6450_0000', 'N51133RL0_6530_0000', 'N51133RL0_6501_0000', 'N51133PL0_6272_0000', 'N51133PL0_6271_0000', 'N51133PL0_6270_0000', 'N51133PL0_6140_0000']


def test_default_CountyWithLoadReductionConstraint_instantiation():
    yo = DataHandlerCountyWithLoadReductionConstraint(savedata2file=False, geoentities=['Adams, PA'])
    # Verify the lrseg list is populated correctly
    assert 'N42001PU0_3000_3090' in yo.LRSEGS


def test_default_LrsegWithCostConstraint_instantiation():
    yo = DataHandlerLrsegWithCostConstraint(savedata2file=False, geoentities=['N51133RL0_6450_0000'])
    # Verify the lrseg list is populated correctly
    assert 'N51133RL0_6450_0000' in yo.LRSEGS


def test_default_LrsegWithLoadReductionConstraint_instantiation():
    yo = DataHandlerLrsegWithLoadReductionConstraint(savedata2file=False, geoentities=['N51133RL0_6450_0000'])
    # Verify the lrseg list is populated correctly
    assert 'N51133RL0_6450_0000' in yo.LRSEGS

def test_default_LrsegWithLoadReductionConstraint_instantiation_inMontgomeryCountyMD():
    yo = DataHandlerLrsegWithLoadReductionConstraint(savedata2file=False, geoentities=['N24031PM0_4640_4820'])
    # N24031PM0_4640_4820 = Cabin John Creek, in Montgomery County

    # Verify the lrseg list is populated correctly
    assert 'N24031PM0_4640_4820' in yo.LRSEGS

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
