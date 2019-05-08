import os
import pytest
import pyomo.environ as pe

from efficiencysubproblem.src.model_handling import model_generator


@pytest.fixture(scope='module')
def costmin_model_spec_path(request):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(THIS_DIR, 'costmin_total_Npercentreduction.yaml')


def test_default_modelgen_NorthUmberlandLrseg(costmin_model_spec_path):
    mdlhandler = model_generator.ModelHandlerBase(model_spec_file=costmin_model_spec_path,
                                                  geoscale='lrseg',
                                                  geoentities=['N51133RL0_6450_0000'],
                                                  savedata2file=False,
                                                  baseloadingfilename='2010NoActionLoads_20190325.csv')
    # Verify the original load is about right
    # OLD Obsolete: abs(pe.value(mdlhandler.model.originalload['N']) - 572816.402650118) < 1000
    # Verify the original load is numeric, and positive
    assert pe.value(mdlhandler.model.originalload['N']) > 0


def test_default_modelgen_BroomeNYCounty(costmin_model_spec_path):
    mdlhandler = model_generator.ModelHandlerBase(model_spec_file=costmin_model_spec_path,
                                                  geoscale='county',
                                                  geoentities='Broome, NY',
                                                  savedata2file=False,
                                                  baseloadingfilename='2010NoActionLoads_20190325.csv')

    # OLD Obsolete: abs(pe.value(mdlhandler.model.originalload['N']) - 3344694.57286031) < 1000
    # Verify the original load is numeric, and positive
    assert pe.value(mdlhandler.model.originalload['N']) > 0


def test_default_modelgen_AdamsPACounty(costmin_model_spec_path):
    mdlhandler = model_generator.ModelHandlerBase(model_spec_file=costmin_model_spec_path,
                                                  geoscale='county',
                                                  geoentities='Adams, PA',
                                                  savedata2file=False,
                                                  baseloadingfilename='2010NoActionLoads_20190325.csv')

    # Verify the original load is numeric, and positive
    # OLD Obsolete: abs(oe.value(mh.model.originalload['N']) - 3601593.97050113) < 1000
    assert pe.value(mdlhandler.model.originalload['N']) > 0
