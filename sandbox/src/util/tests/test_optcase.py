import pytest


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def resource_a(request):
    from sandbox.src.util.OptCase import OptCase
    # Load an OptCase example
    return OptCase.loadexample(name='adamscounty')


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def test_example_populated_correctly(resource_a):
    pass


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def test_empty_matrix_is_empty(resource_a):
    pass
