import unittest

from sandbox.util.decisionspace.decisionspace import DecisionSpace


class TddForDecisionSpace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.decisionspace = DecisionSpace()

        # cls.dataDf = pd.DataFrame({'date': cls.dates,
        #     'count': np.array([3, 7, 4, 66, 9])})

    def test_lrsegids_populated_correctly_in_decisionspace(self):
        self.decisionspace.land.proceed_from_geography_to_decision_space(scale='County', areanames=['Adams, PA'])
        self.assertIn(745, self.decisionspace.land.lrsegids.loc[:, 'lrsegid'].tolist())
