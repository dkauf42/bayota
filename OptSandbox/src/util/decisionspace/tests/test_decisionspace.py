import unittest

from sandbox.util.decisionspace.decisionspace import DecisionSpace


class TddForDecisionSpace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.decisionspace = DecisionSpace.fromgeo(scale='County', areanames=['Adams, PA'])

        # cls.dataDf = pd.DataFrame({'date': cls.dates,
        #     'count': np.array([3, 7, 4, 66, 9])})

    def test_lrsegids_populated_correctly_in_decisionspace(self):
        # self.decisionspace.__generate_decisionspace_using_case_geography(scale='County', areanames=['Adams, PA'])
        self.assertIn(745, self.decisionspace.land.lrsegids.loc[:, 'lrsegid'].tolist())

    def test_animaldecisionspace_only_includes_FEED_loadsource(self):
        # self.decisionspace.__generate_decisionspace_using_case_geography(scale='County', areanames=['Adams, PA'])
        self.assertEqual('Feed', self.decisionspace.animal.nametable.loc[:, 'LoadSourceGroup'].unique()[0])

    def test_manuredecisionspace_only_includes_FEED_loadsource(self):
        # self.decisionspace.__generate_decisionspace_using_case_geography(scale='County', areanames=['Adams, PA'])
        self.assertEqual('Feed', self.decisionspace.manure.nametable.loc[:, 'LoadSourceGroup'].unique()[0])
