import os
import unittest
import numpy as np
import pandas as pd

from sandbox.util.OptCase import OptCase
from sandbox.__init__ import get_outputdir

writedir = get_outputdir()


class TddForOptCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # Load the Source Data and Base Condition tables
        cls.oc = OptCase()
        cls.oc.load_tables()

        cls.oc.name = 'TestOne'
        cls.oc.description = 'TestOneDescription'
        cls.oc.baseyear = '1995'
        cls.oc.basecondname = 'Example_BaseCond2'
        cls.oc.wastewatername = 'Example_WW1'
        cls.oc.costprofilename = 'Example_CostProfile1'
        cls.oc.geoscalename = 'County'
        cls.oc.geoareanames = ['Adams, PA']

        cls.oc.proceed_from_geography_to_decision_space()

        # pd.Series(cls.oc.land_slabnametable.loadsource.unique()).\
        #     to_csv(os.path.join(writedir, 'testwrite_uniqueloadsources.csv'))
        # pd.Series(cls.oc.land_slabnametable.bmpshortname.unique()).\
        #     to_csv(os.path.join(writedir, 'testwrite_uniquebmpshortnames.csv'))
        #
        # cls.oc.land_slabidtable.to_csv(os.path.join(writedir, 'testwrite_lalbidtable.csv'))
        # cls.oc.land_slabnametable.to_csv(os.path.join(writedir, 'testwrite_lalbnametable.csv'))

    def test_sectors_list_is_correct(self):
        self.assertSequenceEqual(self.oc.sectorids.sectorid.tolist(), [1, 2, 3, 4, 5])

    def test_geography_populated_correctly(self):
        self.assertIn('N42001PU2_2790_3290',
                      self.oc.queries.lrsegnames_from(lrsegids=self.oc.lrsegids).landriversegment.tolist())

    def test_agencies_populated_correctly(self):
        pass

    def test_empty_matrix_is_empty(self):
        # ematrix = self.oc.pmatrices['ndas'].eligibleparametermatrix
        # m, n = ematrix.shape
        # self.assertEqual(m*n, np.count_nonzero(ematrix))
        pass
