import pytest

from ..jeeves import Jeeves
from ..sourcehooks.bmp import Bmp

# Load the Source Data and Base Condition tables
source = Jeeves.loadInSourceDataFromSQL()
bmp = Bmp(sourcedata=source)

def test_names_query_contains_GRASSBUFFERS():
    assert 'GrassBuffers' in bmp.all_names().tolist()
