import os
import pytest
import cloudpickle
import pyomo.environ as pyo

from bayom_e.model_handling.interface import build_model


@pytest.fixture(scope='module')
def costmin_model_spec_path(request):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(THIS_DIR, 'costmin_total_Npercentreduction')


def test_default_modelgen_NorthUmberlandLrseg(costmin_model_spec_path):
    model, dataplate = build_model(model_spec_name=costmin_model_spec_path, geoscale='lrseg',
                                   geoentities=['N51133RL0_6450_0000'],
                                   baseloadingfilename='2010NoActionLoads_updated.csv', savedata2file=False)

    # Verify the original load is about right
    # OLD Obsolete: abs(pyo.value(mdlhandler.model.originalload['N']) - 572816.402650118) < 1000
    # Verify the original load is numeric, and positive
    assert pyo.value(model.original_load_expr['N']) > 0


def test_default_modelgen_BroomeNYCounty(costmin_model_spec_path):
    model, dataplate = build_model(model_spec_name=costmin_model_spec_path, geoscale='county', geoentities='Broome, NY',
                                   baseloadingfilename='2010NoActionLoads_updated.csv', savedata2file=False)

    # OLD Obsolete: abs(pyo.value(mdlhandler.model.originalload['N']) - 3344694.57286031) < 1000
    # Verify the original load is numeric, and positive
    assert pyo.value(model.original_load_expr['N']) > 0


def test_default_modelgen_AdamsPACounty(costmin_model_spec_path):
    model, dataplate = build_model(model_spec_name=costmin_model_spec_path, geoscale='county', geoentities='Adams, PA',
                                   baseloadingfilename='2010NoActionLoads_updated.csv', savedata2file=False)

    # Verify the original load is numeric, and positive
    # OLD Obsolete: abs(pyo.value(mh.model.originalload['N']) - 3601593.97050113) < 1000
    assert pyo.value(model.original_load_expr['N']) > 0

def test_expression_pickling_AdamsPA(costmin_model_spec_path):
    model, dataplate = build_model(model_spec_name=costmin_model_spec_path, geoscale='county', geoentities='Adams, PA',
                                   baseloadingfilename='2010NoActionLoads_updated.csv', savedata2file=False)

    pickle_str = cloudpickle.dumps(model.original_load_expr)
    loaded_model_expr = cloudpickle.loads(pickle_str)

    assert [(k, v) for k, v in model.original_load_expr.items()] == \
           [(k, v) for k, v in loaded_model_expr.items()]
