import pytest


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def resource_a(request):
    from sandbox.src.sandboxer import main
    return main


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def test_main_testcase1_runs_to_end_with_valid_arguments(resource_a):
    assert resource_a(numinstances=1, testcase=1).successful_creation_log is True


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def test_main_testcase2_runs_to_end_with_valid_arguments(resource_a):
    assert resource_a(numinstances=1, testcase=2).successful_creation_log is True


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def test_main_testcase3_runs_to_end_with_valid_arguments(resource_a):
    assert resource_a(numinstances=1, testcase=3).successful_creation_log is True


@pytest.mark.skip('sandbox is out-of-date, and not currently usable', allow_module_level=True)
def test_main_raises_error_with_invalid_argument_values(resource_a):
    with pytest.raises(ValueError):
        resource_a(numinstances=1, testcase=5)
