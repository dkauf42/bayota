import os
import pytest
import pyomo.environ as pe

from efficiencysubproblem.src.model_handling import model_generator
from efficiencysubproblem.src.solver_handling import solvehandler


@pytest.fixture(scope='module')
def costmin_modelhandler_for_singlelrseg(request):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))
    costmin_model_spec_path = os.path.join(THIS_DIR, 'costmin_total_Npercentreduction.yaml')
    mdlhandler = model_generator.ModelHandlerBase(model_spec_file=costmin_model_spec_path,
                                                  geoscale='lrseg',
                                                  geoentities=['N51133RL0_6450_0000'],
                                                  savedata2file=False,
                                                  baseloadingfilename='2010NoActionLoads_20190325.csv')
    return mdlhandler


def test_default_modelsolve_singlelrseg(costmin_modelhandler_for_singlelrseg):
    mdlhandler = costmin_modelhandler_for_singlelrseg
    solution_dict = solvehandler.basic_solve(modelhandler=mdlhandler, mdl=mdlhandler.model,
                                             translate_to_cast_format=False)
    assert solution_dict['feasible'] is True
