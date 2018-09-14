import pytest

from ..jeeves import Jeeves
from ..sourcehooks.loadsource import LoadSource

# Load the Source Data and Base Condition tables
source = Jeeves.loadInSourceDataFromSQL()
loadsource = LoadSource(sourcedata=source)


def test_loadsources_query_from_lrseg_agency_sectors_contains_LEGUMEHAY():
    assert 'Legume Hay' in loadsource.loadsources_from_lrseg_agency_sector(lrsegs=['N42001PU2_2790_3290'],
                                                                           agencies=['NONFED', 'FWS'],
                                                                           sectors=['Agriculture']).loadsource.tolist()
