import unittest
import numpy as np

from sandbox.util.OptCase import OptCase


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

        cls.oc.populate_geography_from_scale_and_areas()
        cls.oc.populate_agencies_from_geography()
        cls.oc.populate_sectors()
        print(cls.oc.geography.LandRiverSegment)

        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        cls.oc.generate_emptyparametermatrices()
        cls.oc.mark_eligibility()
        cls.oc.generate_boundsmatrices()

    def test_sectors_list_is_correct(self):
        self.assertSequenceEqual(self.oc.sectors_included,
                                 ['Agriculture', 'Developed', 'Natural', 'Septic', 'Wastewater'])

    def test_empty_matrix_is_empty(self):
        ematrix = self.oc.pmatrices['ndas'].eligibleparametermatrix
        m, n = ematrix.shape
        self.assertEqual(m*n, np.count_nonzero(ematrix))
