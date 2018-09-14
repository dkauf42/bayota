import pytest

from ..jeeves import Jeeves
from ..sourcehooks.sector import Sector

# # Load the Source Data and Base Condition tables
# source = Jeeves.loadInSourceDataFromSQL()
# sector = Sector(sourcedata=source)

@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Sector(sourcedata=source)


def test_sector_names_query(resource_a):
    assert 'Agriculture' in resource_a.all_names().tolist()
