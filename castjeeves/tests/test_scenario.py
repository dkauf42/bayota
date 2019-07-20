import pytest

from castjeeves.jeeves import Jeeves
from castjeeves.sourcehooks import Scenario


@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    source = Jeeves.loadInSourceDataFromSQL()
    return Scenario(sourcedata=source)


def test_get_baseconditionid_2010(resource_a):
    baseconditionid = resource_a.get_baseconditionid(landchangemodelscenario='Historic Trends',
                                                     baseyear='2010')
    assert baseconditionid == 29


def test_get_baseconditionid_2017(resource_a):
    baseconditionid = resource_a.get_baseconditionid(landchangemodelscenario='Current Zoning',
                                                     baseyear='2017')
    assert baseconditionid == 52
