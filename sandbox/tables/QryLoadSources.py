import pandas as pd
import numpy as np

from sandbox.matrices.MatrixBase import MatrixBase


class QryLoadSources:
    def __init__(self, tables=None):
        """Wrapper for Load Source data tables. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """
        self.tables = tables

    def get_yaad_for_sand(self, geographies=None, agencies=None):
        """ get the LoadSources (along with their maxes) for each segment-agency pair
        get_tables_of_load_sources_and_their_units_and_amounts_by_geoagencies

        Returns:
            namedtuple with three dataframes
        """
        lsdev = self._get_sources_in_lrsegs(name='developed', lrsegs=geographies['LandRiverSegment'], agencies=agencies)
        lsnat = self._get_sources_in_lrsegs(name='natural', lrsegs=geographies['LandRiverSegment'], agencies=agencies)
        lsagr = self._get_sources_in_lrsegs(name='agriculture', lrsegs=geographies['LandRiverSegment'], agencies=agencies)
        lssep = self._get_sources_in_lrsegs(name='septic', lrsegs=geographies['LandRiverSegment'], agencies=agencies)
        lsndas = pd.concat([lsnat, lsdev, lsagr, lssep], ignore_index=True)
        """ Hierarchical indices are specified for each dataframe. """
        return lsndas.set_index(['LandRiverSegment', 'Agency', 'LoadSource'], drop=True).copy()

    def get_yaad_for_animal(self, geographies=None):
        """ get the LoadSources (along with their maxes) for each segment-agency pair
        get_tables_of_load_sources_and_their_units_and_amounts_by_geoagencies
        """
        lsani = self._get_sources_in_lrsegs(name='animal', fips=geographies['FIPS'])
        """ Hierarchical indices are specified for each dataframe. """
        return lsani.set_index(['FIPS', 'AnimalName', 'LoadSource'], drop=True).copy()

    def get_yaad_for_manure(self, geographies=None):
        """ get the LoadSources (along with their maxes) for each segment-agency pair
        get_tables_of_load_sources_and_their_units_and_amounts_by_geoagencies
        """
        lsman = self._get_sources_in_lrsegs(name='manure', fips=geographies['FIPS'])
        #  For manure, all the possible FIPSFrom and FIPSTo combinations are generated.
        newdf_manure = MatrixBase.expand_grid({'FIPSFrom': lsman.FIPS.unique(),
                                               'FIPSTo': lsman.FIPS.unique(),
                                               'AnimalName': lsman.AnimalName.unique(),
                                               'LoadSource': lsman.LoadSource.unique()})
        # Put 'Dry_Tons_of_Stored_Manure' column back in the dataframe, aligning with FIPS, AnimalName, & LoadSource
        lsman.rename(columns={'FIPS': 'FIPSFrom'}, inplace=True)
        new_df_merged = pd.merge(lsman.loc[:, ('FIPSFrom', 'AnimalName', 'LoadSource', 'Dry_Tons_of_Stored_Manure')],
                                 newdf_manure, how='left', on=['FIPSFrom', 'AnimalName', 'LoadSource'])

        new_df_merged.set_index(['FIPSFrom', 'FIPSTo', 'AnimalName', 'LoadSource'], drop=True, inplace=True)
        new_df_merged['Amount'] = np.nan  # add Amount as a normal column

        return new_df_merged

    def _get_sources_in_lrsegs(self, lrsegs=None, agencies=None, fips=None, name=''):
        """Get the load sources present (whether zero acres or not) in the specified segment-agencies

        Returns:
            pandas.DataFrame

        Note:
            for ndas, the return DataFrame has columns: [LandRiverSegment, Agency, LoadSource, Amount, Unit]
            for animal, the return DataFrame has columns: [ScenarioName, BaseCondition, FIPS, CountyName,
                                                           StateAbbreviation, AnimalName, LoadSource, AnimalCount,
                                                           AnimalUnits]
            for manure, the return DataFrame has columns: [County, StateAbbreviation, FIPS,
                                                    LoadSource, Dry_Tons_of_Stored_Manure]
        """
        lsdf_geobool = pd.DataFrame()
        lsdf_nongeobool = pd.DataFrame()

        # Find the load sources
        if (name == 'natural') | (name == 'developed') | (name == 'agriculture') | (name == 'septic'):
            print('\nFinding load sources for <%s> in specified LRseg/agencies' % name)
            if (lrsegs is None) | (agencies is None):
                raise ValueError('Either "lrsegs" or "agencies" is None, '
                                 'but must be specified for "%s" load sources' % name)

            if name == 'natural':
                prebmpls_df = self.tables.lsnatural.PreBmpLoadSourceNatural
            elif name == 'developed':
                prebmpls_df = self.tables.lsdeveloped.PreBmpLoadSourceDeveloped
            elif name == 'agriculture':
                prebmpls_df = self.tables.lsagriculture.PreBmpLoadSourceAgriculture
            elif name == 'septic':
                prebmpls_df = self.tables.lsseptic.SepticSystems
            else:
                raise ValueError('unrecognized source type name: "%s"' % name)

            lsdf_geobool['LandRiverSegment'] = prebmpls_df['LandRiverSegment'].isin(lrsegs.unique())
            lsdf_geobool = lsdf_geobool.any(axis=1)
            lsdf_nongeobool['Agency'] = prebmpls_df['Agency'].isin(agencies)
            lsdf_nongeobool = lsdf_nongeobool.any(axis=1)

            lsdf_bool = lsdf_geobool & lsdf_nongeobool
            print('lsdf_nongeobool is %d entries long with %d nonzeros' % (len(lsdf_nongeobool), lsdf_nongeobool.sum()))
            print('lsdf_bool is %d entries long with %d nonzeros' % (len(lsdf_bool), lsdf_bool.sum()))
            filtered_lsdf = prebmpls_df.loc[lsdf_bool, :]

        elif (name == 'animal') | (name == 'manure'):
            print('\nFinding load sources for <%s> in specified County' % name)
            if fips is None:
                raise ValueError('"county" is None, but must be specified for "%s" load sources' % name)

            if name == 'animal':
                prebmpls_df = self.tables.basecond.animalcounts
                countyheader = 'FIPS'
            elif name == 'manure':
                prebmpls_df = self.tables.lsmanure.ManureTonsProduced
                countyheader = 'FIPS'
            else:
                raise ValueError('unrecognized source type name: "%s"' % name)

            lsdf_geobool['FIPS'] = prebmpls_df[countyheader].isin(fips.unique())
            lsdf_geobool = lsdf_geobool.any(axis=1)
            filtered_lsdf = prebmpls_df.loc[lsdf_geobool, :]

        else:
            raise ValueError('unrecognized source type name: "%s"' % name)

        print('lsdf_geobool is %d entries long with %d nonzeros' % (len(lsdf_geobool), lsdf_geobool.sum()))
        return filtered_lsdf.copy()

    @staticmethod
    def containssimilarcol(dataframe, name):
        """
        Returns:
            (1) True/False if the name is represented in one of the column headers of the dataframe
            (2) (list str) name that is represented as a column header of the dataframe
        """
        agencyheader = ['Agency', 'AgencyCode']
        if name in agencyheader:
            dfheadername = [i for i in agencyheader if i in dataframe.columns.tolist()]
            return dataframe.columns.isin(agencyheader).any(), ''.join(dfheadername)
        else:
            dfheadername = [i for i in [name] if i in dataframe.columns.tolist()]
            return dataframe.columns.str.contains(name).any(), ''.join(dfheadername)

    @staticmethod
    def getsimilarcol(dataframe, name):
        agencyheader = ['Agency', 'AgencyCode']
        countyheader = ['CountyName', 'County']
        if name in agencyheader:
            dfheadername = [i for i in agencyheader if i in dataframe.columns.tolist()]
        elif name in countyheader:
            dfheadername = [i for i in countyheader if i in dataframe.columns.tolist()]
        else:
            return dataframe[name]

        return dataframe.loc[:, dataframe.columns.str.contains(''.join(dfheadername))]