import os
import unittest
import numpy as np
import pandas as pd

from sandbox.src.util.OptCase import OptCase
from sandbox.src.__init__ import get_outputdir

writedir = get_outputdir()


class TddForOptCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.oc = OptCase.loadexample(name='adamscounty')

    def test_example_populated_correctly(self):
        pass

    def test_empty_matrix_is_empty(self):
        pass
