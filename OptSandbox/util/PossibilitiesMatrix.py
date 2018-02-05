from scipy import sparse
import pandas as pd
from tqdm import tqdm  # Loop progress indicator module

from filters.SegmentAgencyTypeFilter import SegmentAgencyTypeFilter


def _create_emptydf(row_indices, column_names):
    """ Short module-level function for generating the skeleton of a possibility-matrix"""
    df = pd.DataFrame(index=row_indices, columns=column_names)

    df.sort_index(axis=0, inplace=True, sort_remaining=True)
    df.sort_index(axis=1, inplace=True, sort_remaining=True)

    return df


class PossibilitiesMatrix:
    def __init__(self, tables=None, includespec=None):
        """Filter by Segment-agency_types"""

        # Options are used to query the BaseCondition data and get the Load Sources for each segment-agency pair
        sat = SegmentAgencyTypeFilter(tables=tables, includespec=includespec)

        # A sparse matrix is created for each Segment-Agency-Type table.
        # For the Land table,   the specs are rows=seg-agency-sources X columns=BMPs.
        # For the Animal table, the specs are rows=FIPS-animal-sources X columns=BMPs.
        # For the Manure table, the specs are rows=FIPSto-FIPSfrom-animal-sources X columns=BMPs.
        self.ndas = None
        self.anim = None
        self.manu = None
        self._create_emptymatrices(sat, tables)

        #upper_bounds = self.__identifyhardupperbounds(sat)

        # Get a series of all the LoadSources in this scenario
        allloadsources = pd.concat([self.ndas.index.get_level_values('LoadSource').to_series(),
                                    self.anim.index.get_level_values('LoadSource').to_series(),
                                    self.manu.index.get_level_values('LoadSource').to_series()],
                                   ignore_index=True).unique()
        # A dictionary is generated with <keys:loadsource>, <values:eligible BMPs>.
        self.bmpdict = self._dict_of_bmps_by_loadsource(tables.srcdata, allloadsources)

        # Nonempty markers are generated for eligible (Geo, Agency, Source, BMP) coordinates in the possibilities matrix
        self.geo_seg_source_bmps = None
        self.filter_from_sat(dataframe=self.ndas, srcdataobj=tables.srcdata)
        self.filter_from_sat(dataframe=self.anim, srcdataobj=tables.srcdata)
        self.filter_from_sat(dataframe=self.manu, srcdataobj=tables.srcdata)

        self.ndas.to_csv('./output/testwrite_PossibilitiesMatrix_ndas.csv')
        self.anim.to_csv('./output/testwrite_PossibilitiesMatrix_anim.csv')
        self.manu.to_csv('./output/testwrite_PossibilitiesMatrix_manu.csv')

    def _create_emptymatrices(self, sat, tables):
        # Create a sparse matrix for each sat table with rows=seg-agency-sources X columns=BMPs
        lsndas_indexed = sat.lsndas.set_index(['LandRiverSegment', 'Agency', 'LoadSource']).copy()
        self.ndas = _create_emptydf(row_indices=lsndas_indexed.index, column_names=tables.srcdata.allbmps_shortnames)
        lsani_indexed = sat.lsani.set_index(['FIPS', 'AnimalName', 'LoadSource']).copy()
        self.anim = _create_emptydf(row_indices=lsani_indexed.index, column_names=tables.srcdata.allbmps_shortnames)
        lsman_indexed = sat.lsman.set_index(['FIPS', 'AnimalName', 'LoadSource']).copy()
        self.manu = _create_emptydf(row_indices=lsman_indexed.index, column_names=tables.srcdata.allbmps_shortnames)

    def _dict_of_bmps_by_loadsource(self, srcdataobj, load_sources):
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

        return ls_to_bmp_dict

    def filter_from_sat(self, dataframe, srcdataobj):
        """Find the segment - agency - source combinations available in the specified options.
        """
        # Get all the BMPs that are possible on the set of Load sources
        self.geo_seg_source_bmps = dataframe.copy()
        bmplistoflists = []  # Create a list to store the data
        overallbmplist = []
        totalnumbmps = 0
        n = len(dataframe.index)
        print('>> Generating nonempty markers for eligible (Geo, Agency, Source, BMP) '
              'coordinates in the possibilities matrix')
        loadsourceindex = dataframe.index.names.index('LoadSource')
        for index, row in tqdm(dataframe.iterrows(), total=n):  # iterate through the load sources

            # Mark the eligible BMPs for each Load Source with a 999 instead of a NaN
            bmplist = self.bmpdict[row.name[loadsourceindex]]
            #print(bmplist)
            #dataframe.loc[(index[0], index[1], row.LoadSource), bmplist] = 1
            row.loc[bmplist] = 1

            bmplistoflists.append(bmplist)
            totalnumbmps += len(bmplist)
            overallbmplist += bmplist

        overallbmplist = self.removedups(overallbmplist)
        overallbmptypes = srcdataobj.findbmptype(overallbmplist)
        print('length of overall bmp list: %d' % len(overallbmplist))
        print(overallbmplist)

        diffbmps = set(dataframe.columns.tolist()).symmetric_difference(set(overallbmplist))
        print('- There are %d differences between the possibilities matrix BMPs and OverallBMPlist:' % len(diffbmps))
        print(diffbmps)

        print('- Possibilities matrix dimensions are : %s' % (dataframe.shape,))
        print('- Possibilities matrix is made up of %d nonzero and '
              '%d null elements, out of %d total elements' % (dataframe.sum().sum(),
                                                              dataframe.isnull().sum().sum(),
                                                              dataframe.shape[0] * dataframe.shape[1]))

        self.geo_seg_source_bmps['eligible_bmps'] = bmplistoflists
        print('total no. of eligible BMPs: <%d>' % totalnumbmps)

        #print(self.geo_seg_source_bmps.head())
        #print(bmplist[0])
        self.geo_seg_source_bmps.to_csv('./output/testwrite_PossibilitiesMatrix_geosegsource_bmps.csv')

    def return_sparse(self):  # TODO: unused method, remove.
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

