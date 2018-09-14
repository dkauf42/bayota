import pytest

from ..jeeves import Jeeves
from ..sourcehooks.sourcehooks import SourceHook


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return SourceHook(sourcedata=source)


def test_singleconvert_returns_single_series(resource_a):
    pass


def test_append_ids_to_table(resource_a):
    pass


def test_checkOnlyOne(resource_a):
    pass
