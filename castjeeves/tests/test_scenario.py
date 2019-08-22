import pytest

from castjeeves.sourcehooks import Scenario


@pytest.fixture(scope='module')
def resource_a(request, source_resource):
    return Scenario(sourcedata=source_resource)


def test_get_baseconditionid_2010(resource_a):
    baseconditionid = resource_a.get_baseconditionid(landchangemodelscenario='Historic Trends',
                                                     baseyear='2010')
    assert baseconditionid == 29


def test_get_baseconditionid_2017(resource_a):
    baseconditionid = resource_a.get_baseconditionid(landchangemodelscenario='Current Zoning',
                                                     baseyear='2017')
    assert baseconditionid == 52
