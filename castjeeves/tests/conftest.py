import pytest
from castjeeves.jeeves import Jeeves


@pytest.fixture(scope='session')
def source_resource(request):
    # Load the Source Data and Base Condition tables
    return Jeeves.loadInSourceDataFromSQL()
