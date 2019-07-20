import os
import pytest

from bayom_e.model_handling.interface import build_model
from bayom_e.solver_handling import solvehandler


@pytest.fixture(scope='module')
def costmin_model_for_singlelrseg(request):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    costmin_model_spec_path = os.path.join(THIS_DIR, 'costmin_total_Npercentreduction.yaml')

    model = build_model(model_spec_file=costmin_model_spec_path,
                        geoscale='lrseg',
                        geoentities=['N51133RL0_6450_0000'],
                        savedata2file=False,
                        baseloadingfilename='2010NoActionLoads_updated.csv')
    return model


def test_default_modelsolve_singlelrseg(costmin_model_for_singlelrseg):
    solvername = 'ipopt'
    instance, results, feasible = solvehandler.solve(localsolver=True, solvername=solvername,
                                                     instance=costmin_model_for_singlelrseg)
    assert feasible is True
