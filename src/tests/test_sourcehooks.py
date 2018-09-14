import pytest

from ..jeeves import Jeeves
from ..sourcehooks.sourcehooks import SourceHook

# Load the Source Data and Base Condition tables
source = Jeeves.loadInSourceDataFromSQL()
sourcehook = SourceHook(sourcedata=source)


def test_singleconvert_returns_single_series():
    pass


def test_append_ids_to_table():
    pass


def test_checkOnlyOne():
    pass
