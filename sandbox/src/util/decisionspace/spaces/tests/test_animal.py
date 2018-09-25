import unittest

from sandbox.src.util.decisionspace import DecisionSpace
from sandbox.src.util.decisionspace.spaces.animal import Animal


class TddForAnimal(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        jeeves = DecisionSpace.load_queries()
        cls.animal = Animal(jeeves=jeeves)

    def test_something(self):
        pass
