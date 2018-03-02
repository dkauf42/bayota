import pandas as pd


class QryLoadSources:
    def __init__(self, tables=None):
        """Wrapper for Load Source data tables. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """
        self.tables = tables

    def get_sources_in_lrsegs(self, lrsegs=None, agencies=None, counties=None, name=''):
        """Get the load sources present (whether zero acres or not) in the specified segment-agencies"""
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
            if counties is None:
                raise ValueError('"county" is None, but must be specified for "%s" load sources' % name)

            if name == 'animal':
                prebmpls_df = self.tables.basecond.animalcounts
                countyheader = 'CountyName'
            elif name == 'manure':
                prebmpls_df = self.tables.lsmanure.ManureTonsProduced
                countyheader = 'County'
            else:
                raise ValueError('unrecognized source type name: "%s"' % name)

            lsdf_geobool['CountyName'] = prebmpls_df[countyheader].isin(counties.unique())
            lsdf_geobool = lsdf_geobool.any(axis=1)
            filtered_lsdf = prebmpls_df.loc[lsdf_geobool, :]

        else:
            raise ValueError('unrecognized source type name: "%s"' % name)

        print('lsdf_geobool is %d entries long with %d nonzeros' % (len(lsdf_geobool), lsdf_geobool.sum()))
        return filtered_lsdf

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