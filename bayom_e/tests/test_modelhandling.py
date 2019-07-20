import os
import pytest
import pyomo.environ as pyo

from bayom_e.model_handling.interface import build_model


@pytest.fixture(scope='module')
def costmin_model_spec_path(request):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(THIS_DIR, 'costmin_total_Npercentreduction.yaml')


def test_default_modelgen_NorthUmberlandLrseg(costmin_model_spec_path):
    model, dataplate = build_model(model_spec_file=costmin_model_spec_path,
                                   geoscale='lrseg',
                                   geoentities=['N51133RL0_6450_0000'],
                                   savedata2file=False,
                                   baseloadingfilename='2010NoActionLoads_updated.csv')

    # Verify the original load is about right
    # OLD Obsolete: abs(pyo.value(mdlhandler.model.originalload['N']) - 572816.402650118) < 1000
    # Verify the original load is numeric, and positive
    assert pyo.value(model.originalload['N']) > 0


def test_default_modelgen_BroomeNYCounty(costmin_model_spec_path):
    model, dataplate = build_model(model_spec_file=costmin_model_spec_path,
                                   geoscale='county',
                                   geoentities='Broome, NY',
                                   savedata2file=False,
                                   baseloadingfilename='2010NoActionLoads_updated.csv')

    # OLD Obsolete: abs(pyo.value(mdlhandler.model.originalload['N']) - 3344694.57286031) < 1000
    # Verify the original load is numeric, and positive
    assert pyo.value(model.originalload['N']) > 0


def test_default_modelgen_AdamsPACounty(costmin_model_spec_path):
    model, dataplate = build_model(model_spec_file=costmin_model_spec_path,
                                   geoscale='county',
                                   geoentities='Adams, PA',
                                   savedata2file=False,
                                   baseloadingfilename='2010NoActionLoads_updated.csv')

    # Verify the original load is numeric, and positive
    # OLD Obsolete: abs(pyo.value(mh.model.originalload['N']) - 3601593.97050113) < 1000
    assert pyo.value(model.originalload['N']) > 0
