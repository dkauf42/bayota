import os
import pytest

from bayom_e.model_handling.interface import build_model
from bayom_e.model_handling.model_inspection import get_dataframe_of_original_load_for_each_loadsource


@pytest.fixture(scope='module')
def costmin_model_for_county(request):
    THIS_DIR = os.path.dirname(os.path.abspath(__file__))

    model, dataplate = build_model(model_spec=os.path.join(THIS_DIR, 'costmin_total_Npercentreduction.yaml'),
                                   geoscale='county',
                                   geoentities='Adams, PA',
                                   savedata2file=False,
                                   baseloadingfilename='2010NoActionLoads_updated.csv')

    return model


def test_get_loads_by_loadsource(costmin_model_for_county):
    df = get_dataframe_of_original_load_for_each_loadsource(costmin_model_for_county, 'N')

    columnsarethere = (list(df.columns) == ['index', 'loadsourceshortname', 'v', 'loadsource'])
    itisnotempty = (df.shape[0] > 1)
    aopisthere = any(df['loadsourceshortname'] == 'aop')

    assert ((columnsarethere and itisnotempty) and aopisthere)
