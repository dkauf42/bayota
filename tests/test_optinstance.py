import unittest
import numpy as np

from util import OptInstance


class TddForOptInstance(unittest.TestCase):

    def setUp(self):
        # Load the Source Data and Base Condition tables
        self.oi = OptInstance()
        self.oi.load_tables()

        self.oi.name = 'TestOne'
        self.oi.description = 'TestOneDescription'
        self.oi.baseyear = '1995'
        self.oi.basecondname = 'Example_BaseCond2'
        self.oi.wastewatername = 'Example_WW1'
        self.oi.costprofilename = 'Example_CostProfile1'
        self.oi.geoscalename = 'County'
        self.oi.geoareanames = ['Adams, PA']

        self.oi.geographies_included = self.oi.queries.source. \
            get_lrseg_table(scale=self.oi.geoscalename, areanames=self.oi.geoareanames)
        print(self.oi.geographies_included.LandRiverSegment)
        self.oi.agencies_included = self.oi.queries.base. \
            get_agencies_in_lrsegs(lrsegs=self.oi.geographies_included.LandRiverSegment)
        self.oi.sectors_included = self.oi.queries.source.get_all_sector_names()

        # Generate a emptyparametermatrix with rows(i)=seg-agency-sources X columns(j)=BMPs
        self.oi.generate_emptyparametermatrices()
        self.oi.mark_eligibility()
        self.oi.generate_boundsmatrices()

    def test_sectors_list_is_correct(self):
        self.assertSequenceEqual(self.oi.sectors_included,
                                 ['Agriculture', 'Developed', 'Natural', 'Septic', 'Wastewater'])

    def test_empty_matrix_is_empty(self):
        ematrix = self.oi.pmatrices['ndas'].eligibleparametermatrix
        m, n = ematrix.shape
        self.assertEqual(m*n, np.count_nonzero(ematrix))
