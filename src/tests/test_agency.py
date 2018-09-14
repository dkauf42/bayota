import pytest

from ..jeeves import Jeeves
from ..sourcehooks.agency import Agency

# Load the Source Data and Base Condition tables
source = Jeeves.loadInSourceDataFromSQL()
agency = Agency(sourcedata=source)

def test_agency_names_query():
    assert 'NONFED' in agency.all_names().tolist()

def test_agencies_query_from_lrsegs():
    assert 'NONFED' in agency.agencycodes_from_lrsegnames(lrsegnames=['N42001PU2_2790_3290']).agencycode.tolist()
