from scipy import sparse
import pandas as pd
from tqdm import tqdm  # Loop progress indicator module

from filters.SegmentAgencyTypeFilter import SegmentAgencyTypeFilter


class PossibilitiesMatrix:
    def __init__(self, sourcedataobj=None, optionloaderobj=None, baseconditionobj=None):
        """Filter by Segment-agency_types"""

        # Options are used to query the BaseCondition data and get the Load Sources for each segment-agency pair
        satobj = SegmentAgencyTypeFilter(optionloaderobj=optionloaderobj, baseconditionobj=baseconditionobj)

        # Create a sparse matrix with rows=seg-agency-sources X columns=BMPs
        self.data = None
        self.__create_matrix(satobj, sourcedataobj.allbmps_shortnames)
        self.bmpdict = None
        self.__dict_of_bmps_by_loadsource(sourcedataobj, satobj.all_sat.LoadSource.unique())

        # Get the list of BMPs available on the chosen load sources
        self.geo_seg_source_bmps = None
        self.filter_from_sat(satobj=satobj, srcdataobj=sourcedataobj)

    def __create_matrix(self, satobj, allbmps):
        df = pd.DataFrame(data=satobj.sat_indices, columns=allbmps)

        df.sort_index(axis=0, inplace=True, sort_remaining=True)
        df.sort_index(axis=1, inplace=True, sort_remaining=True)

        self.data = df

    def __dict_of_bmps_by_loadsource(self, srcdataobj, load_sources):
        """ Generate a dictionary of BMPs that are eligible for every load source """
        ls_to_bmp_dict = {}
        for ls in load_sources:
            # Get the Load Source groups that this Load source is in.
            loadsourcegroups = srcdataobj.get(sheetabbrev='sourcegrpcomponents', getcolumn='LoadSourceGroup',
                                              by='LoadSource', equalto=ls)  # pandas.core.series.Series
            bmplist = []  # Create a list to store the data
            for x in loadsourcegroups:  # iterate through the load source groups
                # Get the BMPs that can be applied on this load source group
                thesebmps = srcdataobj.get(sheetabbrev='sourcegrps', getcolumn='BmpShortName',
                                           by='LoadSourceGroup', equalto=x).tolist()
                bmplist += thesebmps

            bmplist = self.removedups(bmplist)
            ls_to_bmp_dict[ls] = bmplist

        self.bmpdict = ls_to_bmp_dict

    def filter_from_sat(self, satobj, srcdataobj):
        """Find the segment - agency - source combinations available in the specified options.
        """
        # Get all the BMPs that are possible on the set of Load sources
        self.geo_seg_source_bmps = satobj.all_sat.copy()
        bmplistoflists = []  # Create a list to store the data
        overallbmplist = []
        totalnumbmps = 0
        n = len(satobj.all_sat.index)
        print('Generating nonzero markers for eligible SAT-B combinations in the possibilities matrix')
        for index, row in tqdm(satobj.all_sat.iterrows(), total=n):  # iterate through the load sources

            # Mark the eligible BMPs for each Load Source with a 999 instead of a NaN
            bmplist = self.bmpdict[row.LoadSource]
            self.data.loc[(index[0], index[1], row.LoadSource), bmplist] = 1

            bmplistoflists.append(bmplist)
            totalnumbmps += len(bmplist)
            overallbmplist += bmplist

        overallbmplist = self.removedups(overallbmplist)
        overallbmptypes = srcdataobj.findbmptype(overallbmplist)
        print('length of overall bmp list: %d' % len(overallbmplist))
        print(overallbmplist)

        diffbmps = set(self.data.columns.tolist()).symmetric_difference(set(overallbmplist))
        print('- There are %d differences between the possibilities matrix BMPs and OverallBMPlist:' % len(diffbmps))
        print(diffbmps)

        print('- Possibilities matrix dimensions are : %s' % (self.data.shape,))
        print('- Possibilities matrix is made up of %d nonzero and '
              '%d null elements, out of %d total elements' % (self.data.sum().sum(),
                                                              self.data.isnull().sum().sum(),
                                                              self.data.shape[0] * self.data.shape[1]))

        self.geo_seg_source_bmps['eligible_bmps'] = bmplistoflists
        print('total no. of eligible BMPs: <%d>' % totalnumbmps)

        # Load Reduction BMPs
        # TODO: Get data from

        # Animal BMPs
        # TODO: Get data from BaseCondition 'Animal Counts' spreadsheet

        # Manure BMPs
        # TODO: Get data from ManureTonsProduced spreadsheet

        # Septic Systems
        # TODO: Get data from BaseCondition 'Septic Systems' spreadsheet

        #print(self.geo_seg_source_bmps.head())
        #print(bmplist[0])
        self.geo_seg_source_bmps.to_csv('testwrite_geo_seg_source_bmps.csv')

    def return_sparse(self):
        sparsedf = sparse.coo_matrix(self.data.fillna(0))
        print('Density of sparse matrix is %f' % (sparsedf.getnnz() / (sparsedf.shape[0] * sparsedf.shape[1])))
        return sparsedf

    @staticmethod
    def removedups(listwithduplicates):
        """ Code to remove duplicate elements"""
        final_list = []
        for num in listwithduplicates:
            if num not in final_list:
                final_list.append(num)
        return final_list

