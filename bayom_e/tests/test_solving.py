import os
import pytest

from bayom_e.model_handling.interface import build_model
from bayom_e.solver_handling import solvehandler


@pytest.fixture(scope='module')
def costmin_model_for_singlelrseg(request):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    costmin_model_spec_path = os.path.join(THIS_DIR, 'costmin_total_Npercentreduction.yaml')

    model, dataplate = build_model(model_spec_name=costmin_model_spec_path, geoscale='lrseg',
                                   geoentities=['N51133RL0_6450_0000'],
                                   baseloadingfilename='2010NoActionLoads_updated.csv', savedata2file=False)
    return model


def test_default_modelsolve_singlelrseg(costmin_model_for_singlelrseg):
    solvername = 'ipopt'
    instance, results, feasible = solvehandler.solve(localsolver=True, solvername=solvername,
                                                     instance=costmin_model_for_singlelrseg)
    assert feasible is True
