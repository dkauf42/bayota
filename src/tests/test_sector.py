import pytest

from ..jeeves import Jeeves
from ..sourcehooks.sector import Sector

# Load the Source Data and Base Condition tables
source = Jeeves.loadInSourceDataFromSQL()
sector = Sector(sourcedata=source)


def test_sector_names_query():
    assert 'Agriculture' in sector.all_names().tolist()
