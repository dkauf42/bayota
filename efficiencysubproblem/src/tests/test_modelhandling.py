import pytest
import pyomo.environ as oe

from efficiencysubproblem.src.model_handling.interface import *


def test_default_LrsegWithCostConstraint_instantiation_NorthUmberlandLrseg():
    mh = get_loaded_model_handler(objectivetype='costmin',
                                  geoscale='lrseg',
                                  geoentities=['N51133RL0_6450_0000'],
                                  savedata2file=False)
    # Verify the original load is about right
    assert abs(oe.value(mh.model.originalload['N51133RL0_6450_0000', 'N']) - 572816.402650118) < 1000


def test_default_CountyWithCostConstraint_instantiation_BroomeNYCounty():
    mh = get_loaded_model_handler(objectivetype='costmin',
                                  geoscale='county',
                                  geoentities=['Broome, NY'],
                                  savedata2file=False)
    # Verify the original load is about right
    assert abs(oe.value(mh.model.originalload['N']) - 3344694.57286031) < 1000


def test_default_CountyWithCostConstraint_instantiation_AdamsPACounty():
    mh = get_loaded_model_handler(objectivetype='costmin',
                                  geoscale='county',
                                  geoentities=['Adams, PA'],
                                  savedata2file=False)
    # Verify the original load is about right
    assert abs(oe.value(mh.model.originalload['N']) - 3601593.97050113) < 1000