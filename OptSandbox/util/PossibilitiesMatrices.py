import pandas as pd
import numpy as np
from tqdm import tqdm  # Loop progress indicator module

from tables.MatrixBase import MatrixBase


class PossibilitiesMatrices:
    def __init__(self, optinstance=None):
        """Filter by Segment-agency_types

        Args:
            optinstance (obj): This is the optimization instance

        Attributes:
            ndas (obj):
            anim (obj):
            manu (obj):

        """
        # Determine what will comprise the rows (indices of load source names) of the possibility matrix
        loadsources = optinstance.queries.loadsources.\
            get_load_sources_in_geoagencies(geographies=optinstance.geographies_included,
                                            agencies=optinstance.agencies_included)
        lsndas_indexed = loadsources.ndas.set_index(['LandRiverSegment', 'Agency', 'LoadSource']).copy()
        lsani_indexed = loadsources.animal.set_index(['FIPS', 'AnimalName', 'LoadSource']).copy()
        #  For manure, all the possible FIPSFrom and FIPSTo combinations are generated.
        newdf_manure = MatrixBase.expand_grid({'FIPSFrom': loadsources.manure.FIPS.unique(),
                                        'FIPSTo': loadsources.manure.FIPS.unique(),
                                        'AnimalName': loadsources.manure.AnimalName.unique(),
                                        'LoadSource': loadsources.manure.LoadSource.unique()})
        newdf_manure_indexed = newdf_manure.set_index(['FIPSFrom', 'FIPSTo', 'AnimalName', 'LoadSource']).copy()
        newdf_manure_indexed['Amount'] = np.nan  # add Amount as a normal column

        """ A sparse matrix is created for each Segment-Agency-Type table.
        The Specs:
            Land: rows=seg-agency-sources X columns=BMPs.
            Animal: rows=FIPS-animal-sources X columns=BMPs
            Manure: rows=FIPSto-FIPSfrom-animal-sources X columns=BMPs
        """
        self.ndas = MatrixBase(name='ndas', row_indices=lsndas_indexed.index,
                               column_names=optinstance.tables.srcdata.allbmps_shortnames)
        self.anim = MatrixBase(name='anim', row_indices=lsani_indexed.index,
                               column_names=optinstance.tables.srcdata.allbmps_shortnames)
        self.manu = MatrixBase(name='manu', row_indices=newdf_manure_indexed.index,
                               column_names=optinstance.tables.srcdata.allbmps_shortnames)

        # NonNaN markers are generated for eligible (Geo, Agency, Source, BMP) coordinates in the possibilities matrix
        self.mark_eligible_coordinates(dataframe=self.ndas.matrix, optinstance=optinstance)
        self.mark_eligible_coordinates(dataframe=self.anim.matrix, optinstance=optinstance)
        self.mark_eligible_coordinates(dataframe=self.manu.matrix, optinstance=optinstance)

        #  TODO: upper_bounds = self._identifyhardupperbounds(sat)
        # Associate a hard lower and upper bound with each marker coordinate in the matrix

        self.ndas.matrix.to_csv('./output/testwrite_PossibilitiesMatrix_ndas.csv')
        self.anim.matrix.to_csv('./output/testwrite_PossibilitiesMatrix_anim.csv')
        self.manu.matrix.to_csv('./output/testwrite_PossibilitiesMatrix_manu.csv')

    def mark_eligible_coordinates(self, dataframe=None, optinstance=None):
        """Generate nonNaN markers for eligible (Geo, Agency, Source, BMP) coordinates in the possibilities matrix

        Args:
            dataframe (pandas.DataFrame):
            optinstance (obj):
        """
        # A dictionary is generated with <keys:loadsource>, <values:eligible BMPs>.
        bmpdict = self._dict_of_bmps_by_loadsource(srcdataobj=optinstance.tables.srcdata)

        # Get all the BMPs that are possible on the set of Load sources
        geo_seg_source_bmps = dataframe.copy()
        bmplistoflists = []  # Create a list to store the data
        overallbmplist = []
        totalnumbmps = 0
        n = len(dataframe.index)
        print('>> Generating nonempty markers for eligible (Geo, Agency, Source, BMP) '
              'coordinates in the possibilities matrix')
        loadsourceindex = dataframe.index.names.index('LoadSource')
        for index, row in tqdm(dataframe.iterrows(), total=n):  # iterate through the load sources
            # Mark the eligible BMPs for each Load Source with a '1' instead of a NaN
            bmplist = bmpdict[row.name[loadsourceindex]]
            row.loc[bmplist] = 1

            bmplistoflists.append(bmplist)
            totalnumbmps += len(bmplist)
            overallbmplist += bmplist

        overallbmplist = self.removedups(overallbmplist)
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

        geo_seg_source_bmps['eligible_bmps'] = bmplistoflists
        print('total no. of eligible BMPs: <%d>' % totalnumbmps)

        geo_seg_source_bmps.to_csv('./output/testwrite_PossibilitiesMatrix_geosegsource_bmps.csv')

    @staticmethod
    def removedups(listwithduplicates):
        """ Code to remove duplicate elements"""
        final_list = []
        for num in listwithduplicates:
            if num not in final_list:
                final_list.append(num)
        return final_list

    def _dict_of_bmps_by_loadsource(self, srcdataobj=None):
        """ Generate a dictionary of BMPs that are eligible for every load source """

        # Get a series of all the LoadSources in this scenario
        all_load_sources = pd.concat([self.ndas.matrix.index.get_level_values('LoadSource').to_series(),
                                      self.anim.matrix.index.get_level_values('LoadSource').to_series(),
                                      self.manu.matrix.index.get_level_values('LoadSource').to_series()],
                                     ignore_index=True).unique()
        ls_to_bmp_dict = {}
        for ls in all_load_sources:
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

