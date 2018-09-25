import pytest

from sandbox.src.util.decisionspace import DecisionSpace
from sandbox.src.util.decisionspace.spaces.animal import Animal

@pytest.fixture(scope='module')
def resource_a(request):
    # Load the Source Data and Base Condition tables
    jeeves = DecisionSpace.load_queries()
    return Animal(jeeves=jeeves)


def test_something(resource_a):
        pass
