import pytest

from sandbox.src.util.decisionspace.decisionspace import DecisionSpace


@pytest.fixture(scope='module')
def resource_a(request):
    # Load a decision space for one county
    decisionspace = DecisionSpace.fromgeo(scale='County', areanames=['Adams, PA'],
                                          baseyear='2013', basecondname='Historic Trends')
    return decisionspace


def test_lrsegids_populated_correctly_in_decisionspace(resource_a):
    assert 745 in resource_a.land.lrsegids.loc[:, 'lrsegid'].tolist()
    # self.decisionspace.__generate_decisionspace_using_case_geography(scale='County', areanames=['Adams, PA'])


def test_animaldecisionspace_only_includes_FEED_loadsource(resource_a):
    assert 'Feed' == resource_a.animal.nametable.loc[:, 'LoadSourceGroup'].unique()[0]
    # self.decisionspace.__generate_decisionspace_using_case_geography(scale='County', areanames=['Adams, PA'])


def test_manuredecisionspace_only_includes_FEED_loadsource(resource_a):
    assert 'Feed' == resource_a.manure.nametable.loc[:, 'LoadSourceGroup'].unique()[0]
    # self.decisionspace.__generate_decisionspace_using_case_geography(scale='County', areanames=['Adams, PA'])
