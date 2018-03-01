import pandas as pd


class SegmentAgencyTypeFilter:
    def __init__(self, tables=None, optinstance=None):
        """Find the load sources (along with their maxes {acres, miles, units, etc.}) in the specified SATs

        Parameters:
            tables (obj):
            optinstance (obj):

        Attributes:
            lsani (pandas dataframe)
            lsman (pandas dataframe)
            lsndas (pandas dataframe)

        Note:
            option headers =
                [BaseCondition, LandRiverSegment, CountyName, StateAbbreviation,
                StateBasin, OutOfCBWS, AgencyCode, Sector]

        """
        # Loop through tables
        # (lsnatural, lsdeveloped, lsagriculture, lsmanure, lsanimal (basecond for now), lsmanure)
        self._lsnat = self._filter_from_options(optinstance, name='natural',
                                                prebmpls_df=tables.lsnatural.PreBmpLoadSourceNatural)
        self._lsdev = self._filter_from_options(optinstance, name='developed',
                                                prebmpls_df=tables.lsdeveloped.PreBmpLoadSourceDeveloped)
        self._lsagr = self._filter_from_options(optinstance, name='agriculture',
                                                prebmpls_df=tables.lsagriculture.PreBmpLoadSourceAgriculture)
        self._lssep = self._filter_from_options(optinstance, name='septic',
                                                prebmpls_df=tables.lsseptic.SepticSystems)
        self.lsani = self._filter_animals_from_options(optinstance, name='animal',
                                                       prebmpls_df=tables.basecond.animalcounts)
        self.lsman = self._filter_animals_from_options(optinstance, name='manure',
                                                       prebmpls_df=tables.lsmanure.ManureTonsProduced)

        self.lsndas = pd.concat([self._lsnat, self._lsdev, self._lsagr, self._lssep], ignore_index=True)

    def _filter_animals_from_options(self, optinstance, name='', prebmpls_df=None):
        """Find the load sources in the specified SATs within a prebmpls_df

        Note:
            option headers = BaseCondition, LandRiverSegment, CountyName,
                StateAbbreviation, StateBasin,
                OutOfCBWS, AgencyCode, Sector

        """
        print('\nFinding load sources for <%s> in specified County' % name)
        # For Animals and Manure, we only need to filter by County (geographically) and not any agencies
        lsdf_geobool = pd.DataFrame()
        valuestoinclude = self.getsimilarcol(optinstance.geographies_included, 'CountyName')
        lsdf_geobool['CountyName'] = self.getsimilarcol(prebmpls_df, 'CountyName').\
            isin(valuestoinclude['CountyName'].unique())
        lsdf_geobool = lsdf_geobool.any(axis=1)
        # Filtering by Agency is not needed for Animals and Manure?!
        print('lsdf_geobool is %d entries long with %d nonzeros' % (len(lsdf_geobool), lsdf_geobool.sum()))
        filtered_lsdf = prebmpls_df.loc[lsdf_geobool, :]

        return filtered_lsdf

    def _filter_from_options(self, optinstance, name='', prebmpls_df=None):
        """Find the load sources in the specified SATs within a prebmpls_df

        Note:
            option headers = BaseCondition, LandRiverSegment, CountyName,
                StateAbbreviation, StateBasin,
                OutOfCBWS, AgencyCode, Sector
        """
        print('\nFinding load sources for <%s> in specified LRseg/agencies' % name)
        # First figure out the filtering by Geography
        geo_options_list = ['LandRiverSegment', 'CountyName', 'StateAbbreviation', 'StateBasin']
        geocolumnstofilterby = prebmpls_df.columns[prebmpls_df.columns.isin(geo_options_list)].tolist()
        print('This PreBMPLoadSource table needs geo filtering by "%s"' % geocolumnstofilterby)
        lsdf_geobool = pd.DataFrame()
        for h in geocolumnstofilterby:
            valuestoinclude = optinstance.geographies_included[h]
            lsdf_geobool[h] = prebmpls_df[h].isin(valuestoinclude)
        lsdf_geobool = lsdf_geobool.any(axis=1)

        # Then figure out filtering by Agency
        non_geo_options_list = ['Agency']
        nongeocolumnstofilterby = prebmpls_df.columns[prebmpls_df.columns.isin(non_geo_options_list)].tolist()
        print('This PreBMPLoadSource table needs non-geo filtering by "%s"' % nongeocolumnstofilterby)
        lsdf_nongeobool = pd.DataFrame()
        for h in nongeocolumnstofilterby:
            #print(optinstance.agencies_included)
            #print(type(optinstance.agencies_included))
            #valuestoinclude = self.getsimilarcol(pd.Series(optinstance.agencies_included).to_frame(), h)
            #valuestoinclude = tables.agencytranslate_fromcodes(valuestoinclude['AgencyCode'])
            valuestoinclude = optinstance.agencies_included
            lsdf_nongeobool[h] = prebmpls_df[h].isin(valuestoinclude)
        lsdf_nongeobool = lsdf_nongeobool.any(axis=1)

        #print(lsdf_geobool)
        #print(lsdf_nongeobool)

        lsdf_bool = lsdf_geobool & lsdf_nongeobool
        print('lsdf_geobool is %d entries long with %d nonzeros' % (len(lsdf_geobool), lsdf_geobool.sum()))
        print('lsdf_nongeobool is %d entries long with %d nonzeros' % (len(lsdf_nongeobool), lsdf_nongeobool.sum()))
        print('lsdf_bool is %d entries long with %d nonzeros' % (len(lsdf_bool), lsdf_bool.sum()))
        filtered_lsdf = prebmpls_df.loc[lsdf_bool, :]

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
