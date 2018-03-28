import unittest
import numpy as np

from sandbox.util.OptCase import OptCase


class TddForOptCase(unittest.TestCase):

    def setUp(self):
        # Load the Source Data and Base Condition tables
        self.oc = OptCase()
        self.oc.load_tables()

        self.oc.name = 'TestOne'
        self.oc.description = 'TestOneDescription'
        self.oc.baseyear = '1995'
        self.oc.basecondname = 'Example_BaseCond2'
        self.oc.wastewatername = 'Example_WW1'
        self.oc.costprofilename = 'Example_CostProfile1'
        self.oc.geoscalename = 'County'
        self.oc.geoareanames = ['Adams, PA']

        self.oc.populate_geography_from_scale_and_areas()
        self.oc.populate_agencies_from_geography()
        self.oc.populate_sectors()
        print(self.oc.geography.LandRiverSegment)

        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.oc.generate_emptyparametermatrices()
        self.oc.mark_eligibility()
        self.oc.generate_boundsmatrices()

    def test_sectors_list_is_correct(self):
        self.assertSequenceEqual(self.oc.sectors_included,
                                 ['Agriculture', 'Developed', 'Natural', 'Septic', 'Wastewater'])

    def test_empty_matrix_is_empty(self):
        ematrix = self.oc.pmatrices['ndas'].eligibleparametermatrix
        m, n = ematrix.shape
        self.assertEqual(m*n, np.count_nonzero(ematrix))
