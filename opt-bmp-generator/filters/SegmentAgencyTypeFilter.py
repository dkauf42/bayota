import pandas as pd
import numpy as np


class SegmentAgencyTypeFilter:
    def __init__(self, tables=None, includespec=None):
        """Find the segment - agency - source combinations available in the specified options."""

        """Find the load sources (along with their maxes {acres, miles, units, etc.}) in the specified SATs
                    option headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
                                     OutOfCBWS, AgencyCode, Sector
        """
        # Loop through tables (lsnatural, lsdeveloped, lsagriculture, lsmanure, lsanimal (basecond for now), lsmanure)
        self.lsnat = self.__filter_from_options(includespec, tables,
                                                prebmpls_df=tables.lsnatural.PreBmpLoadSourceNatural)
        self.lsdev = self.__filter_from_options(includespec, tables,
                                                prebmpls_df=tables.lsdeveloped.PreBmpLoadSourceDeveloped)
        self.lsagr = self.__filter_from_options(includespec, tables,
                                                prebmpls_df=tables.lsagriculture.PreBmpLoadSourceAgriculture)
        self.lssep = self.__filter_from_options(includespec, tables,
                                                prebmpls_df=tables.lsseptic.SepticSystems)
        self.lsani = self.__filter_animals_from_options(includespec,
                                                        prebmpls_df=tables.basecond.animalcounts)
        self.lsman = self.__filter_animals_from_options(includespec,
                                                        prebmpls_df=tables.lsmanure.ManureTonsProduced)

        print('********ANIMAL********')
        print(self.lsani.head())
        print('********MANURE********')
        print(self.lsman.head())

        self.lsndas = pd.concat([self.lsnat, self.lsdev, self.lsagr, self.lssep], ignore_index=True)
        print('********LSNDAS********')
        print(self.lsndas.head())
        #self.lsndas = pd.concat([self.lsnat['LoadSource'],
        #                         self.lsdev['LoadSource'],
        #                         self.lsagr['LoadSource'],
        #                         self.lssep['LoadSource']], ignore_index=True)

        # pd.concat([self.lsnat['LoadSource'],
        #            self.lsdev['LoadSource'],
        #            self.lsagr['LoadSource'],
        #            self.lssep['LoadSource'],
        #            self.lsani['LoadSource'],
        #            self.lsman['LoadSource']], ignore_index=True)

    # def __filter_from_PreBMP_tables(self, tables, includespec):
    #     """Find the load sources (along with their maxes {acres, miles, units, etc.}) in the specified SATs
    #
    #         option headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
    #                          OutOfCBWS, AgencyCode, Sector
    #     """
    #
    #     # Loop through tables (lsnatural, lsdeveloped, lsagriculture, lsmanure, lsanimal (basecond for now), lsmanure)
    #     self.lsnat = self.__filter_from_options(includespec, tables,
    #                                             prebmpls_df=tables.lsnatural.PreBmpLoadSourceNatural)
    #     self.lsdev = self.__filter_from_options(includespec, tables,
    #                                             prebmpls_df=tables.lsdeveloped.PreBmpLoadSourceDeveloped)
    #     self.lsagr = self.__filter_from_options(includespec, tables,
    #                                             prebmpls_df=tables.lsagriculture.PreBmpLoadSourceAgriculture)
    #     self.lssep = self.__filter_from_options(includespec, tables,
    #                                             prebmpls_df=tables.lsseptic.SepticSystems)
    #     self.lsani = self.__filter_animals_from_options(includespec,
    #                                                     prebmpls_df=tables.basecond.animalcounts)
    #     self.lsman = self.__filter_animals_from_options(includespec,
    #                                                     prebmpls_df=tables.lsmanure.ManureTonsProduced)
    #
    #     print('********NATURAL********')
    #     print(self.lsnat.head())
    #     print('********DEVELOPED********')
    #     print(self.lsdev.head())
    #     print('********AGRICULTURE********')
    #     print(self.lsagr.head())
    #     print('********SEPTIC********')
    #     print(self.lssep.head())
    #     print('********ANIMAL********')
    #     print(self.lsani.head())
    #     print('********MANURE********')
    #     print(self.lsman.head())

    def __filter_animals_from_options(self, includespec, prebmpls_df):
        """Find the load sources in the specified SATs within a prebmpls_df

            option headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
                             OutOfCBWS, AgencyCode, Sector
        """
        # For Animals and Manure, we only need to filter by County (geographically) and not any agencies
        lsdf_geobool = pd.DataFrame()
        valuestoinclude = self.getsimilarcol(includespec.geo, 'CountyName')
        lsdf_geobool['CountyName'] = self.getsimilarcol(prebmpls_df, 'CountyName').\
            isin(valuestoinclude['CountyName'].unique())
        lsdf_geobool = lsdf_geobool.any(axis=1)
        # Filtering by Agency is not needed for Animals and Manure?!
        # print('lsdf_geobool is %d entries long with %d nonzeros' % (len(lsdf_geobool), lsdf_geobool.sum()))
        filtered_lsdf = prebmpls_df.loc[lsdf_geobool, :]

        return filtered_lsdf

    def __filter_from_options(self, includespec, tables, prebmpls_df):
        """Find the load sources in the specified SATs within a prebmpls_df

            option headers = BaseCondition, LandRiverSegment, CountyName, StateAbbreviation, StateBasin,
                             OutOfCBWS, AgencyCode, Sector
        """

        # First figure out the filtering by Geography
        geo_options_list = ['LandRiverSegment', 'CountyName', 'StateAbbreviation', 'StateBasin']
        geocolumnstofilterby = prebmpls_df.columns[prebmpls_df.columns.isin(geo_options_list)].tolist()
        # print('This PreBMPLoadSource table needs geo filtering by "%s"' % geocolumnstofilterby)
        lsdf_geobool = pd.DataFrame()
        for h in geocolumnstofilterby:
            valuestoinclude = includespec.geo[h]
            lsdf_geobool[h] = prebmpls_df[h].isin(valuestoinclude)
        lsdf_geobool = lsdf_geobool.any(axis=1)

        # Then figure out filtering by Agency
        non_geo_options_list = ['Agency']
        nongeocolumnstofilterby = prebmpls_df.columns[prebmpls_df.columns.isin(non_geo_options_list)].tolist()
        # print('This PreBMPLoadSource table needs non-geo filtering by "%s"' % nongeocolumnstofilterby)
        lsdf_nongeobool = pd.DataFrame()
        for h in nongeocolumnstofilterby:
            valuestoinclude = self.getsimilarcol(includespec.agency.to_frame(), h)
            valuestoinclude = tables.agencytranslate_fromcodes(valuestoinclude['AgencyCode'])
            lsdf_nongeobool[h] = prebmpls_df[h].isin(valuestoinclude)
        lsdf_nongeobool = lsdf_nongeobool.any(axis=1)

        lsdf_bool = lsdf_geobool & lsdf_nongeobool
        # print('lsdf_bool is %d entries long with %d nonzeros' % (len(lsdf_bool), lsdf_bool.sum()))
        filtered_lsdf = prebmpls_df.loc[lsdf_bool, :]

        return filtered_lsdf

        """
        # Land Use Acres
        # Generate boolean mask for the prebmpls_df based on the option specifications
        # i.e. loop through headers specified in the options file
        oh = optionsobj.headers
        booldf = pd.DataFrame()
        for h in oh:
            optionscolumn = optionsobj.options[h]

            # Convert between similar header names
            #if h == 'AgencyCode'
            #prebmpls_df.columns

            #if prebmpls_df.columns.str.contains(h).any():
            headerindf, dfheadername = self.containssimilarcol(prebmpls_df, h)
            print(h)
            print(headerindf)
            print(dfheadername)
            #print(headerindf)
            #print(dfheadername)
            if (optionscolumn[0] == 'all') | optionscolumn.isnull().values.all():
                # exclude this column from the boolean prebmpls_df mask if we're just going to get all of the values
                print('yo')
                pass
            else:
                print('hello')
                if headerindf:
                    # generate boolean mask for each basecondition row, if its value is in this options column
                    #booldf[h] = prebmpls_df[h].isin(optionscolumn)
                    print('hey')
                    booldf[h] = self.getsimilarcol(prebmpls_df, h).isin(optionscolumn)
        print(booldf.head())

        """
        """Note: For the geographic options (LandRiverSegment, CountyName, StateAbbreviation, StateBasin),
              we want to include rows that are logical ORs of these column values

              For example, if options include {County: Anne Arundel, State: DE, StateBasin: WV James River Basin},
              then we want to include load sources from all of those places, not just the intersection of them.

              Then, we want the logical AND of those geooptions with the other options
                                                                        (BaseCondition, OutOfCBWS, AgencyCode, Sector)

              Then, we want logical AND of those options with the load sources that have non-zero values
        """
        """

        # A logical OR amongst the geographic options is computed.
        countyheaderindf, countyheadername = self.containssimilarcol(prebmpls_df, 'CountyName')
        geo_options_list = ('LandRiverSegment', 'CountyName', 'StateAbbreviation', 'StateBasin')
        # TODO: deal with case when 'CountyName' is not present
        geooptionsbooldf = booldf[booldf.columns[booldf.columns.isin(geo_options_list)]]
        print(booldf)
        geooptionsbool = geooptionsbooldf.any(axis=1)
        print(geooptionsbool)

        # A logical AND between the geo-options result and the non-geo-options is computed.
        nongeooptionsbooldf = booldf[booldf.columns.difference(geooptionsbooldf.columns)]
        optionsbool = geooptionsbool & nongeooptionsbooldf.all(axis=1)

        agencyheaderindf, agencyheadername = self.containssimilarcol(prebmpls_df, 'AgencyCode')
        if agencyheaderindf:
            # self.all_sat
            print(optionsbool.shape)
            print(prebmpls_df.shape)
            filtered_df = prebmpls_df.loc[optionsbool, ['LandRiverSegment', agencyheadername, 'LoadSource']].copy()
            filtered_df = filtered_df.set_index(['LandRiverSegment', agencyheadername])
            #self.all_sat.to_csv('testwrite_allsegsources.csv')
            print('All seg+agency specific load sources: %d' % np.sum(optionsbool))

            # self.sat_indices
            filtered_df_indices = prebmpls_df.loc[optionsbool, ['LandRiverSegment', agencyheadername, 'LoadSource']].copy()
            filtered_df_indices = filtered_df_indices.set_index(['LandRiverSegment', agencyheadername, 'LoadSource'])
            #self.sat_indices.to_csv('testwrite_sat_indices.csv')
        else:
            # self.all_sat
            filtered_df = prebmpls_df.loc[optionsbool, ['LandRiverSegment', 'LoadSource']].copy()
            filtered_df = filtered_df.set_index(['LandRiverSegment'])
            #self.all_sat.to_csv('testwrite_allsegsources.csv')
            print('All seg+agency specific load sources: %d' % np.sum(optionsbool))

            # self.sat_indices
            filtered_df_indices = prebmpls_df.loc[optionsbool, ['LandRiverSegment', 'LoadSource']].copy()
            filtered_df_indices = filtered_df_indices.set_index(['LandRiverSegment', 'LoadSource'])
            #self.sat_indices.to_csv('testwrite_sat_indices.csv')

        return filtered_df
        """

    @staticmethod
    def containssimilarcol(dataframe, name):
        """Returns
        (1) True/False if the name is represented in one of the column headers of the dataframe
        (2) <list str> name that is represented as a column header of the dataframe
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
