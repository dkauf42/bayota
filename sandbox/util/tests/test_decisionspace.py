import unittest

from sandbox.util.DecisionSpaces import DecisionSpace


class TddForDecisionSpace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.decisionspace = DecisionSpace()

        cls.dataDf = pd.DataFrame({'date': cls.dates,
            'count': np.array([3, 7, 4, 66, 9])})

    def test_something(self):
        pass
