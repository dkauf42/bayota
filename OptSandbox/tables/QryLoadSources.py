import pandas as pd


class QryLoadSources:
    def __init__(self, tables=None):
        """Wrapper for Load Source data tables. Provides methods for querying different information

        Attributes:
            tables (obj): location where table objects are written to file to speed up re-runs

        """
        self.tables = tables

    def get_sources_in_lrsegs(self, lrsegs=None, agencies=None, counties=None, name=''):  # TODO replace the SATFilter._filter_from_options() method with this method
        """Get the load sources present (whether zero acres or not) in the specified segment-agencies"""
        lsdf_geobool = pd.DataFrame()
        lsdf_nongeobool = pd.DataFrame()

        # Find the load sources
        if (name == 'natural') | (name == 'developed') | (name == 'agriculture') | (name == 'septic'):
            if name == 'natural':
                prebmpls_df = self.tables.lsnatural.PreBmpLoadSourceNatural
            elif name == 'developed':
                prebmpls_df = self.tables.lsdeveloped.PreBmpLoadSourceDeveloped
            elif name == 'agriculture':
                prebmpls_df = self.tables.lsagriculture.PreBmpLoadSourceAgriculture
            elif name == 'septic':
                prebmpls_df = self.tables.lsseptic.SepticSystems
            else:
                raise ValueError('unrecognized source type name: <%s>' % name)

            print('\nFinding load sources for <%s> in specified LRseg/agencies' % name)

            lsdf_geobool['LandRiverSegment'] = prebmpls_df['LandRiverSegment'].isin(lrsegs)
            lsdf_geobool = lsdf_geobool.any(axis=1)

            lsdf_nongeobool['Agency'] = prebmpls_df['Agency'].isin(agencies)
            lsdf_nongeobool = lsdf_nongeobool.any(axis=1)

            lsdf_bool = lsdf_geobool & lsdf_nongeobool
            print('lsdf_geobool is %d entries long with %d nonzeros' % (len(lsdf_geobool), lsdf_geobool.sum()))
            print('lsdf_nongeobool is %d entries long with %d nonzeros' % (len(lsdf_nongeobool), lsdf_nongeobool.sum()))
            print('lsdf_bool is %d entries long with %d nonzeros' % (len(lsdf_bool), lsdf_bool.sum()))
            filtered_lsdf = prebmpls_df.loc[lsdf_bool, :]

        elif (name == 'animal') | (name == 'manure'):
            if name == 'animal':
                prebmpls_df = self.tables.basecond.animalcounts
            elif name == 'manure':
                prebmpls_df = self.tables.lsmanure.ManureTonsProduced
            else:
                raise ValueError('unrecognized source type name: <%s>' % name)

            print('\nFinding load sources for <%s> in specified County' % name)

            # For Animals and Manure, we only need to filter by County (geographically) and not any agencies
            lsdf_geobool['CountyName'] = self.getsimilarcol(prebmpls_df, 'CountyName').isin(counties)
            lsdf_geobool = lsdf_geobool.any(axis=1)
            # Filtering by Agency is not needed for Animals and Manure?!
            print('lsdf_geobool is %d entries long with %d nonzeros' % (len(lsdf_geobool), lsdf_geobool.sum()))
            filtered_lsdf = prebmpls_df.loc[lsdf_geobool, :]
        else:
            raise ValueError('unrecognized source type name: <%s>' % name)

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