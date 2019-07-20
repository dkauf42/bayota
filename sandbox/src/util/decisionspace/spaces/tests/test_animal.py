import pytest


@pytest.fixture(scope='module')
def resource_a(request):
    from sandbox.src.util.decisionspace import DecisionSpace
    from sandbox.src.util.decisionspace.spaces.animal import Animal
    # Load the Source Data and Base Condition tables
    jeeves = DecisionSpace.load_queries()
    return Animal(jeeves=jeeves)


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def test_something(resource_a):
        pass
