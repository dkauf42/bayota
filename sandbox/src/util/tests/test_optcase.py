import os
import pytest
import numpy as np
import pandas as pd

from sandbox.src.util.OptCase import OptCase

@pytest.fixture(scope='module')
def resource_a(request):
    # Load an OptCase example
    return OptCase.loadexample(name='adamscounty')


def test_example_populated_correctly(resource_a):
    pass


def test_empty_matrix_is_empty(resource_a):
    pass
